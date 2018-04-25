from django.urls import path

from .views import UserLoginAPI

urlpatterns = [
    path('login', UserLoginAPI.as_view(), name="user_login_api"),
]
