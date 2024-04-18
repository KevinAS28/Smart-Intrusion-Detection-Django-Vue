app_name = 'token_authentication'

from atexit import register
from django.urls import path
from .views import *


urlpatterns = [
    path('get-token', get_token),
    path('refresh-token', refresh_token),
    path('delete-token', delete_token),
    path('register-user', register_user),
    path('create-role', create_role),
    
    
]