from django.urls import path, re_path

from announce.views import UserLoginAPI, GoodsAPI

urlpatterns = [
    path('login', UserLoginAPI.as_view(), name="user_login_api"),
    # path('goods', GoodsAPI.as_view(), name="goods_api"),
    re_path(r'^goods(/(?P<good_id>[0-9]+))?$', GoodsAPI.as_view(), name="goods_api"),
    # path('goods/<int:good_id>', GoodsAPI.as_view(), name="goods_api"),
]
