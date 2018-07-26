from django.urls import path

from api import views

urlpatterns = [
    path('goods/list', views.goods_list),
]
