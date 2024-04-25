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
from intrusion_detection.utils import *
from intrusion_detection.rtdetr import RTDETROnnxDeploy, is_bbox_intersection, line_to_box
from token_authentication.auth_core import token_auth, token_get
from token_authentication import models as ta_models

SystemLog.objects.all().delete()

rtdetr_model = None
if (settings.DEBUG and settings.ISRUNNING_DEVSERVER) or not settings.DEBUG:    
    print('Loading default model...')
    default_rtdetr_model = RTDETROnnxDeploy(model_path=os.path.join(settings.BASE_DIR, 'rtdetr_yolov9bb_ep27.onnx'), classes_labels=os.path.join(settings.BASE_DIR, 'inference_class_labels.json'), sample_img=cv2.imread(os.path.join(settings.BASE_DIR, 'img.jpg')))
    user_models = dict()
    user_streams = dict()

def custom_object_warnings(frame, lines, all_slb, objects_to_warn=['person'], invert=False, user=None):
    # print('custom_object_warnings(0):', lines, objects_to_warn)
    all_crossed_objects = []
    for s, l, b in all_slb:
      for ln in lines:
          ln_type, ln = ln[0], ln[1:]    
          ln_bbox = line_to_box(ln, frame.shape, line_type=ln_type, invert=invert) 
        #   print('custom_object_warnings(1):', l, invert, b, ln_bbox, objects_to_warn, l in objects_to_warn, is_bbox_intersection(b, ln_bbox))
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

def gen(video_source, postprocessor_index, stored=False):
    while True:
        if not stored:
            frame = video_source.get_live_frame(postprocessor_index=postprocessor_index)
        else:
            frame = video_source.get_stored_frame(postprocessor_index=postprocessor_index)
        if not frame:
            print('finish stream')
            break
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        time.sleep(0.1)

def multi_gen(multi_video_source):
    while True:
        frames = multi_video_source.multi_stream()
        
        frame_data = {
            f"frame{i+1}":base64.b64encode(cv2.resize(frames[i], (300,300)).tobytes()).decode('utf-8') for i in range(len(frames))
        } 
        yield (b'--frame\r\n\r\n'
                b'Content-Type: application/json\r\n\r\n' + 
                json.dumps(frame_data).encode('utf-8')
                + b'\r\n\r\n')
        # yield json.dumps(frame_data).encode('utf-8')
        
def multi_frames_stream(request):
    video_sources = MultiVideoSourceFile(['/home/kevin/smart_intrusion_detection/django_smart_intrusion_detection/tmp/bike1.mp4', '/home/kevin/smart_intrusion_detection/django_smart_intrusion_detection/tmp/bike2.mp4'])
    response = StreamingHttpResponse(multi_gen(video_sources), content_type='multipart/x-mixed-replace;boundary=frame')
    response.headers['Access-Control-Allow-Origin'] = '*'  # Adjust for your specific origin if needed
    response.headers['Cache-Control'] = 'no-cache'
    return response    


@token_auth(roles=['*'], get_user=True)        
def video_live_stream(user:ta_models.UserAuthentication, request):
    if not (user.username in user_models):
        user_models[user.username] = default_rtdetr_model
    
    postprocessor_index = int(request.GET['postprocessor_index'])
    stored_stream = request.GET['stored']=='1'
    
    home_settings, inference_settings = user_settings(user)                          
    
    user_model = user_models[user.username].update_parameters(model_to_dict(inference_settings))
    cuslog(user, f'Model settings for {user.username}:', user_models[user.username].get_parameters())
    user_model.obj_warning = lambda frame, all_slb: custom_object_warnings(frame=frame, lines=inference_settings.get_lines(orient=True), all_slb=all_slb, objects_to_warn=inference_settings.objects_to_warn, invert=inference_settings.get_line_invert(), user=user)    
    
    if not user.username in user_streams:
        cuslog(user, 'creating new user stream...')
        video_path = str(home_settings.video_file)
        if not os.path.isfile(video_path):
            user_streams[user.username] = NotFoundSource(text=f'Please choose a video file',size=inference_settings.size)
        else:
            user_streams[user.username] = VideoSourceFile(video_path, postprocessors=[user_model.inference_frame, lambda frame: frame])
        video_source = user_streams[user.username]
    else:
        cuslog(user, 'using existing user stream...')
        video_source = user_streams[user.username]
        
    response = StreamingHttpResponse(gen(video_source, postprocessor_index=postprocessor_index, stored=stored_stream),
                    content_type='multipart/x-mixed-replace; boundary=frame')
    response.headers['Cache-Control'] = 'no-cache'
    return response

@token_auth(roles=['*'], get_user=True)
def update_settings(user, request):         
    if not (user.username in user_models):
        user_models[user.username] = default_rtdetr_model
    
    home_settings, inference_settings = user_settings(user)              
    
    new_settings = json.loads(request.POST['new_settings'])
    cuslog(user, 'new settings:', new_settings)
    
    # handle update backend settings
    for setting_key, setting_val in new_settings['backend_view'].items():
        if setting_key=='new_video_file' and setting_val:
            cuslog(user, 'processing video file...')
            uploaded_file = request.FILES['video_file']
            video_path = os.path.join(settings.MEDIA_DIR_PATH, uploaded_file.name)
            with open(video_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)  
            home_settings.video_file = video_path 
            if user.username in user_streams:
                del user_streams[user.username]
        
    home_settings.save()                     
    
    # handle update inference settings
    
    if 'model_name' in new_settings['inference']:
        new_settings['inference']['model_path'] = settings.INTRUSION_DETECTION_MODELS[new_settings['inference']['model_name']]
        
    new_inference_settings = {k:v for k,v in new_settings['inference'].items() if not (v is None)}
    inference_settings = update_dict(inference_settings, new_inference_settings)
    inference_settings.save()
    user_models[user.username].update_parameters(new_inference_settings)   
    user_models[user.username].obj_warning = lambda frame, all_slb: custom_object_warnings(frame=frame, lines=inference_settings.get_lines(orient=True), all_slb=all_slb, objects_to_warn=inference_settings.objects_to_warn, invert=inference_settings.get_line_invert(), user=user)    
    
    cuslog(user, 'updated inference ML model params:', user_models[user.username].get_parameters())
    cuslog(user, 'updated inference DB model ', model_to_dict(inference_settings))
    
    print('done')
    return JsonResponse({'status': 'ok'})


@token_auth(roles=['*'], get_user=True)
def get_user_settings(user, request):    
    home_settings, inference_settings = user_settings(user)
    settings = {
        'home_settings': model_to_dict(home_settings),
        'inference_settings': model_to_dict(inference_settings)
    }
    if 'keys' in request.GET:
        for k in request.GET['keys'].split(','):
            settings = settings[k]
            
    
    return JsonResponse(settings, safe=False)

def get_model_list(request):
    model_list = list(settings.INTRUSION_DETECTION_MODELS.keys())
    formatted_model_list = [{'id': i+1, 'name': model_list[i]}  for i in range(len(model_list))]
    return JsonResponse(formatted_model_list, safe=False)


@token_auth(roles=['*'], get_user=True)
def get_status(user, request):
    all_warnings = WarningNotification.objects.filter(user=user)
    logs = SystemLog.objects.filter(user=user).order_by('created_at')
    if len(logs)>100:
        [l.delete() for l in logs[:100]]
        logs = SystemLog.objects.filter(user=user).order_by('created_at')
    all_status = {
        'warnings': [custom_model2todict(model=model, request=request, statics=['frame_path']) for model in all_warnings],
        'logs': [log.logtext for log in logs]
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

def login(request):
    username = request.POST['username']
    password = request.POST['password']
    token = token_get(username, password)
    return JsonResponse({'token': token})