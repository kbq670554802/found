from time import strftime

from django.contrib import auth
from django.contrib.admin import exceptions
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from account.models import User
from django.core.paginator import Paginator

from announce.api import APIView, validate_serializer
from announce.models import Goods
from announce.serializers import UserLoginSerializer, GoodsSerializer, PaginatorBaseSerializer, GoodsListSerializer, \
    GoodsEditValidate
import requests
import json


class UserLoginAPI(APIView):
    @validate_serializer(UserLoginSerializer)
    def post(self, request):
        """
        User login api
        """
        data = request.data
        user = auth.authenticate(username=data["username"], password=data["password"])
        if user:
            return self.success("Succeeded")
            user = User()
            user.groups
            group = Group()
            l = list()
            l.append()
        else:
            return self.error("Invalid username or password")

    def get(self, request):
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
            return self.fail(msg='连接微信服务器异常')
        except requests.exceptions.Timeout:
            return self.fail(msg='连接微信服务器异常')

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
            return self.success(msg='登录成功', data=token[0].key)
        else:
            return self.fail(msg='登录失败')


class GoodsAPI(APIView):
    @authentication_classes((TokenAuthentication, BasicAuthentication))
    @permission_classes((IsAuthenticated,))
    @validate_serializer(GoodsEditValidate)
    def post(self, request, good_id):
        data = request.data
        try:
            serializer = GoodsEditValidate(data=data)
            if serializer.is_valid():
                serializer.save()
                return self.success(msg='发布成功')
            return self.fail(msg='提交失败,请重新提交')
        except Exception as e:
            return self.fail(msg='服务器故障,提交失败')

    @validate_serializer(GoodsEditValidate)
    def put(self, request, good_id):
        data = request.data
        try:
            goods = Goods.objects.get(pk=good_id)
        except Goods.DoesNotExist:
            return self.fail(msg='失物信息不存在')

        try:
            # data.id = good_id
            serializer = GoodsEditValidate(goods, data=data)
            if serializer.is_valid():
                serializer.save()
                return self.success(msg='修改成功')
            return self.fail(msg='提交失败,请重新保存')
        except Exception as e:
            return self.fail(msg='服务器故障,保存失败')

    def get(self, request, good_id):
        if good_id is None:
            # 获取列表
            data = request.data
            page_index = data.get('page_index', 1)
            page_size = data.get('page_size', 10)
            type = data.get('type', 0)
            goods_list = Goods.objects.filter(type=type).order_by('-create_time')
            paginator = Paginator(goods_list, page_size)
            goods_page = paginator.page(page_index)
            result = GoodsListSerializer(goods_page.object_list, many=True).data
            data = self.result_list(result_list=result, page_size=page_size, page_index=page_index
                                    , page_count=paginator.num_pages, total_count=paginator.count,
                                    has_more=goods_page.has_next())
            return self.success(msg='获取失物列表信息成功', data=data)
        else:
            # 获取单个失物信息
            try:
                goods = Goods.objects.get(pk=good_id)
            except Goods.DoesNotExist:
                return self.fail(msg='失物信息不存在')
            return self.success(msg='获取失物信息成功', data=GoodsEditValidate(goods).data)

    def delete(self, request, good_id):
        try:
            Goods.objects.get(pk=good_id).delete()
        except Goods.DoesNotExist:
            return self.fail(msg='失物信息不存在')
        return self.success(msg='删除失物信息成功')
