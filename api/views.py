from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from announce.models import Goods
from announce.serializers import GoodsListSerializer
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

    # paginator = Paginator(goods_list, page_size)
    # goods_page = paginator.page(page_index)
    # result = GoodsListSerializer(goods_page.object_list, many=True).data
    # data = self.result_list(result_list=result, page_size=page_size, page_index=page_index
    #                         , page_count=paginator.num_pages, total_count=paginator.count,
    #                         has_more=goods_page.has_next())

    return JsonResponse.paging(goods_list, request, GoodsListSerializer)
    # return self.success(msg='获取失物列表信息成功', data=data)
