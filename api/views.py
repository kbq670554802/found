from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from announce.models import Goods
from announce.serializers import GoodsListSerializer, GoodsDetailSerializer
from api.serializer.serializers import UserSerializer
from api.utils.response import JsonResponse
import requests
import json


@api_view()
def wechat_login(request):
    # https: // api.weixin.qq.com / sns / jscode2session?appid = wx834124f7e433edd6 & secret = 9
    # aeb2a0c6a812874867071ad74b1e5c2 & js_code = 0713
    # mO2b1lZvJu0v8X3b1hHS2b13mO2L & grant_type = authorization_code

    data = request.data
    params = {
        'appid': 'wx834124f7e433edd6',
        'secret': '9aeb2a0c6a812874867071ad74b1e5c2',
        'js_code': data.get('code', ''),
        'grant_type': 'authorization_code'
    }
    try:
        r = requests.get('https://api.weixin.qq.com/sns/jscode2session', params=params, )
    except requests.exceptions.ConnectTimeout:
        return JsonResponse(code=-1, msg='连接微信服务器异常')
    except requests.exceptions.Timeout:
        return JsonResponse(code=-1, msg='连接微信服务器异常')

    if r.status_code == 200:
        content = json.loads(r.text)
        openid = content.get('openid', '')
        try:
            user = User.objects.get(openid=openid)
        except User.DoesNotExist:
            user = User()
            user.openid = openid
            user.save()
        session_key = content.get('session_key', '')
        # token = Token.objects.create(user=user)
        token = Token.objects.get_or_create(user=user)
        return JsonResponse(data=token[0].key, msg='登录成功')
    else:
        return JsonResponse(code=-1, msg='登录失败')


@api_view()
def goods_list(request):
    type = request.GET.get('type', 0)
    goods_list = Goods.objects.filter(type=type).order_by('-create_time')
    return JsonResponse.paging(goods_list, request, GoodsListSerializer)


@api_view(['POST'])
def goods_add_or_update(request):
    try:
        id = int(request.data['id'])
    except Exception:
        id = 0

    serializer = GoodsDetailSerializer(data=request.data)
    from account.models import User
    user = User.objects.get(pk=1)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=user)
    return JsonResponse(msg='保存成功')


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def goods_delete(request):
    # from account.models import User
    # user = User.objects.get(pk=2)
    # token = Token.objects.create(user=user)
    try:
        id = int(request.data['id'])
        if id <= 0:
            return JsonResponse(code=-1, msg='失物Id非法')
    except Exception:
        return JsonResponse(code=-1, msg='失物Id非法')

    try:
        Goods.objects.get(pk=id, user=request.user).delete()
        return JsonResponse(msg='删除成功')
    except Goods.DoesNotExist:
        return JsonResponse(code=-1, msg='信息不存在或者不是您发布的')
