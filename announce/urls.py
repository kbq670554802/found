from django.urls import path

from announce.views import UserLoginAPI, GoodsAPI

urlpatterns = [
    path('login', UserLoginAPI.as_view(), name="user_login_api"),
    path('goods/<int:good_id>', GoodsAPI.as_view(), name="goods_api"),
]
