from django.contrib.auth.models import User
from django.urls import path

from api import views

urlpatterns = [
    path('user/wechat_login', views.wechat_login),
    path('goods/list', views.goods_list),
    path('goods/add_or_update', views.goods_add_or_update),
    path('goods/detail', views.goods_detail),
    path('goods/delete', views.goods_delete),
]
