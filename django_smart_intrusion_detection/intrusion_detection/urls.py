"""smartdetectoralarm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from intrusion_detection.views import *

app_name = 'intrusion_detection'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('videostream/', video_stream),
    path('updatesettings/', update_settings),
    path('modellist/', get_model_list),
    path('usersettings/', get_user_settings),
    path('usersettings/', get_user_settings),
    path('clearwarning/', clear_obj_warning),
    path('status/', get_status),
]
