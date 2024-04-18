import time
import os
import json

import cv2

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.forms.models import model_to_dict

from intrusion_detection.models import *
from intrusion_detection.video_source import *
from intrusion_detection.rtdetr import RTDETROnnxDeploy
from token_authentication.auth_core import token_auth
from token_authentication import models as ta_models


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
    user_model = update_dict(user_models[user.username], model_to_dict(inference_settings))

    home_settings = HomeSettings.objects.filter(user=user)
    if len(home_settings)==0:
        home_settings = HomeSettings(user=user)    
    else:
        home_settings = home_settings[0]
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
    user_models[user.username].update_parameters(new_inference_settings)   
    inference_settings.save()
    
    print('updated inference params:', user_models[user.username].get_parameters())
    
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
    
# Create your views here.
