from django.urls import path

from api import views

urlpatterns = [
    path('goods/list', views.goods_list),
    path('goods/add_or_update', views.goods_add_or_update),
    path('goods/detail', views.goods_detail),
    path('goods/delete', views.goods_delete),
]
