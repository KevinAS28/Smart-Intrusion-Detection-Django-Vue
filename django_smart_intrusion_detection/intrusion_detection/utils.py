import os
import base64

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.forms.models import model_to_dict

from intrusion_detection.models import *

def custom_model2todict(model, request=None, files=[], statics=[], hiddens=['created_at', 'updated_at'], timestamps=['created_at', 'updated_at']):
    model_dict = model_to_dict(model)
    for fa in files:
        if os.path.isfile(fa):
            with open(fa, 'rb') as file:
                model_dict[fa] = base64.b64encode(file.read()).decode("utf-8")
    for hid in hiddens:
        model_dict[hid] = getattr(model, hid)
    for stat in statics:
        # print(request.scheme, request.get_host(), settings.MEDIA_DIR, getattr(model, stat))
        static_url = staticfiles_storage.url(os.path.basename(getattr(model, stat)))
        model_dict[stat] =  f"{request.build_absolute_uri('/')}{static_url}"
    for ts in timestamps:
        model_dict[ts] = getattr(model, ts).timestamp()
    return model_dict


def update_dict(dict0, dict1):
    for key, val in dict1.items():
        if hasattr(dict0, key):
            setattr(dict0, key, val)
    return dict0

def user_settings(user):
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
        
    return home_settings, inference_settings

def cuslog(user, *txt):
    txt = ' '.join([str(i) for i in txt])
    print(txt)
    SystemLog(user=user,logtext=txt).save()
    