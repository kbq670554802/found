import json

import requests
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from account.models import User
from announce.models import Goods
from announce.serializers import GoodsListSerializer, GoodsDetailSerializer
from api.serializer.serializers import UserSerializer
from api.utils.response import JsonResponse


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
        token = Token.objects.get_or_create(user=user)
        return JsonResponse(data=token[0].key, msg='登录成功')
    else:
        return JsonResponse(code=-1, msg='登录失败')


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def user_update(request):
    user = request.user
    serializer = UserSerializer(user, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return JsonResponse(msg='修改成功')


@api_view()
def goods_list(request):
    try:
        type = int(request.query_params['type'])
        if type <= 0:
            return JsonResponse(code=-1, msg='类型非法')
    except Exception:
        return JsonResponse(code=-1, msg='类型非法')

    goods_list = Goods.objects.filter(type=type).order_by('-create_time')
    return JsonResponse.paging(goods_list, request, GoodsListSerializer)


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def goods_add_or_update(request):
    try:
        id = int(request.data['id'])
    except Exception:
        id = 0

    if id > 0:  # 更新
        try:
            goods = Goods.objects.get(pk=id, user=request.user)
        except Goods.DoesNotExist:
            return JsonResponse(code=-1, msg='信息不存在或者不是您发布的')
        serializer = GoodsDetailSerializer(goods, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse(msg='修改成功')
    else:  # 新增
        if request.data.get('id') == 0:
            del request.data['id']
        serializer = GoodsDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return JsonResponse(msg='添加成功')


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def goods_delete(request):
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


@api_view(['GET'])
def goods_detail(request):
    try:
        id = int(request.query_params['id'])
        if id <= 0:
            return JsonResponse(code=-1, msg='失物Id非法')
    except Exception:
        return JsonResponse(code=-1, msg='失物Id非法')

    try:
        goods = Goods.objects.get(pk=id)
        serializer = GoodsDetailSerializer(goods)
        return JsonResponse(serializer.data, msg='失物详情')
    except Goods.DoesNotExist:
        return JsonResponse(code=-1, msg='信息不存在')
