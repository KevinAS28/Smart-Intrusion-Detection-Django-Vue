import time
import os
import json
import base64

import cv2

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.forms.models import model_to_dict
from django.contrib.staticfiles.storage import staticfiles_storage

from intrusion_detection.models import *
from intrusion_detection.video_source import *
from intrusion_detection.rtdetr import RTDETROnnxDeploy, is_bbox_intersection, line_to_box
from token_authentication.auth_core import token_auth
from token_authentication import models as ta_models

def custom_object_warnings(frame, lines, all_slb, objects_to_warn=['person'], invert=False, user=None):
    print('custom_object_warnings(0):', lines, objects_to_warn)
    all_crossed_objects = []
    for s, l, b in all_slb:
      for ln in lines:
          ln_type, ln = ln[0], ln[1:]    
          ln_bbox = line_to_box(ln, frame.shape, line_type=ln_type, invert=invert) 
          print('custom_object_warnings(1):', l, b, ln_bbox, objects_to_warn, l in objects_to_warn, is_bbox_intersection(b, ln_bbox))
          obj_crossed = False
          if l in objects_to_warn:
              obj_crossed = is_bbox_intersection(b, ln_bbox)
              if obj_crossed:
                print(f'WARNING: OBJECT {l} HAS CROSSED THE LINE')      
                all_crossed_objects.append(l)

    if len(all_crossed_objects)>0:
        existing_warn_notif = WarningNotification.objects.filter(user=user)
        if len(existing_warn_notif)==0:
            frame_path = os.path.join(settings.MEDIA_DIR_PATH, f'{user.username}_{str(time.time())}.jpg')
            cv2.imwrite(frame_path, frame)        
            warn_notif = WarningNotification(user=user, objs=','.join(all_crossed_objects), frame_path=frame_path)        
            warn_notif.save()

rtdetr_model = None
if (settings.DEBUG and settings.ISRUNNING_DEVSERVER) or not settings.DEBUG:    
    print('Loading default model...')
    default_rtdetr_model = RTDETROnnxDeploy(model_path=os.path.join(settings.BASE_DIR, 'rtdetr_yolov9bb_ep27.onnx'), classes_labels=os.path.join(settings.BASE_DIR, 'inference_class_labels.json'), sample_img=cv2.imread(os.path.join(settings.BASE_DIR, 'img.jpg')))
    user_models = dict()


def gen(video_source):
    while True:
        frame = video_source.get_frame()
        if not frame:
            print('finish stream')
            break
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        time.sleep(0.1)

def update_dict(dict0, dict1):
    for key, val in dict1.items():
        if hasattr(dict0, key):
            setattr(dict0, key, val)
    return dict0

@token_auth(roles=['*'], get_user=True)        
def video_stream(user:ta_models.UserAuthentication, request):
    if not (user.username in user_models):
        user_models[user.username] = default_rtdetr_model
    
    inference_settings = InferenceSettings.objects.filter(user=user)
    if len(inference_settings)==0:
        inference_settings = InferenceSettings(user=user)         
    else:
        inference_settings = inference_settings[0]
        
    home_settings = HomeSettings.objects.filter(user=user)
    if len(home_settings)==0:
        home_settings = HomeSettings(user=user)    
    else:
        home_settings = home_settings[0]
                
    user_model = update_dict(user_models[user.username], model_to_dict(inference_settings))
    print(f'Model settings for {user.username}:', user_models[user.username].get_parameters())
    user_model.obj_warning = lambda frame, all_slb: custom_object_warnings(frame=frame, lines=inference_settings.get_lines(orient=True), all_slb=all_slb, objects_to_warn=inference_settings.objects_to_warn, invert=inference_settings.get_line_invert(), user=user)    

    video_path = str(home_settings.video_file)
    if not os.path.isfile(video_path):
        video_source = NotFoundSource(text=f'Please choose a video file',size=inference_settings.size)
    else:
        video_source = VideoSourceFile(video_path, postprocessor=user_model.inference_frame)
    response = StreamingHttpResponse(gen(video_source),
                    content_type='multipart/x-mixed-replace; boundary=frame')
    response.headers['Cache-Control'] = 'no-cache'
    return response

@token_auth(roles=['*'], get_user=True)
def update_settings(user, request):         
    if not (user.username in user_models):
        user_models[user.username] = default_rtdetr_model
                   
    new_settings = json.loads(request.POST['new_settings'])
    print('new settings:', new_settings)
    # handle update backend settings
    home_settings = HomeSettings.objects.filter(user=user)
    if len(home_settings)==0:
        home_settings = HomeSettings(user=user)    
    else:
        home_settings = home_settings[0]
    for setting_key, setting_val in new_settings['backend_view'].items():
        if setting_key=='new_video_file' and setting_val:
            print('processing video file...')
            uploaded_file = request.FILES['video_file']
            video_path = os.path.join(settings.MEDIA_DIR_PATH, uploaded_file.name)
            with open(video_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)  
            home_settings.video_file = video_path 
        
    home_settings.save()                     
    
    # handle update inference settings
    inference_settings = InferenceSettings.objects.filter(user=user)
    if len(inference_settings)==0:
        inference_settings = InferenceSettings(user=user)         
    else:
        inference_settings = inference_settings[0]
    if 'model_name' in new_settings['inference']:
        new_settings['inference']['model_path'] = settings.INTRUSION_DETECTION_MODELS[new_settings['inference']['model_name']]
        del new_settings['inference']['model_name']
    new_inference_settings = {k:v for k,v in new_settings['inference'].items() if not (v is None)}
    inference_settings = update_dict(inference_settings, new_inference_settings)
    inference_settings.save()
    user_models[user.username].update_parameters(new_inference_settings)   
    user_models[user.username].obj_warning = lambda frame, all_slb: custom_object_warnings(frame=frame, lines=inference_settings.get_lines(orient=True), all_slb=all_slb, objects_to_warn=inference_settings.objects_to_warn, invert=inference_settings.get_line_invert(), user=user)    
    
    print('updated inference ML model params:', user_models[user.username].get_parameters())
    print('updated inference DB model ', model_to_dict(inference_settings))
    
    print('done')
    return JsonResponse({'status': 'ok'})

def get_model_list(request):
    model_list = list(settings.INTRUSION_DETECTION_MODELS.keys())
    formatted_model_list = [{'id': i+1, 'name': model_list[i]}  for i in range(len(model_list))]
    return JsonResponse(formatted_model_list, safe=False)

@token_auth(roles=['*'], get_user=True)
def get_user_settings(user, request):
    home_settings = dict()
    inference_settings = dict()
    if len(HomeSettings.objects.filter(user=user))>0:
        home_settings = model_to_dict(HomeSettings.objects.get(user=user))
    if len(InferenceSettings.objects.filter(user=user))>0:
        inference_settings = model_to_dict(InferenceSettings.objects.get(user=user))        
    settings = {
        'home_settings': home_settings,
        'inference_settings': inference_settings
    }
    return JsonResponse(settings)

def custom_model2todict(model, request=None, files=[], statics=[], hiddens=['created_at', 'updated_at']):
    model_dict = model_to_dict(model)
    for fa in files:
        if os.path.isfile(fa):
            with open(fa, 'rb') as file:
                model_dict[fa] = base64.b64encode(file.read()).decode("utf-8")
    for hid in hiddens:
        model_dict[hid] = getattr(model, hid)
    for stat in statics:
        # print(request.scheme, request.get_host(), settings.MEDIA_DIR, getattr(model, stat))
        model_dict[stat] =  f"{request.scheme}://{request.get_host()}{os.path.join(settings.MEDIA_DIR, getattr(model, os.path.basename(stat)))}"
    return model_dict

@token_auth(roles=['*'], get_user=True)
def get_status(user, request):
    all_warnings = WarningNotification.objects.filter(user=user)
    all_status = {
        'warnings': [custom_model2todict(model=model, request=request, statics=['frame_path']) for model in all_warnings],
        
    }
    return JsonResponse(all_status)

@token_auth(roles=['*'], get_user=True)
def clear_obj_warning(user, request):
    all_warnings = WarningNotification.objects.filter(user=user)
    for warn in all_warnings:
        frame_path = warn.frame_path
        if os.path.isfile(frame_path):
            os.remove(frame_path)
        warn.delete()
    return JsonResponse({'deleted': len(all_warnings)})
