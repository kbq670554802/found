from time import strftime

from django.contrib import auth
from django.contrib.auth.models import User

from announce.api import APIView, validate_serializer
from announce.models import Goods
from announce.serializers import UserLoginSerializer, GoodsSerializer


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


class GoodsAPI(APIView):
    def post(self, request):
        data = request.data
        goods = Goods()
        goods.title = data.get('title', '')
        goods.content = data.get('content', '')
        goods.lost_address = data.get('lost_address', '')
        goods.contact_address = data.get('contact_address', '')
        goods.phone = data.get('phone', '')
        goods.save()
        return self.success(message='发布成功')

    def put(self, request, good_id):
        data = request.data
        try:
            goods = Goods.objects.get(pk=good_id)
        except Goods.DoesNotExist:
            return self.fail(message='失物信息不存在')
        if not data.get('title', None) is None:
            goods.title = data.get('title', '')
        if not data.get('content', None) is None:
            goods.content = data.get('content', '')
        if not data.get('lost_address', None) is None:
            goods.lost_address = data.get('lost_address', '')
        if not data.get('contact_address', None) is None:
            goods.contact_address = data.get('contact_address', '')
        if not data.get('phone', None) is None:
            goods.phone = data.get('phone', '')
        goods.save()
        return self.success(message='修改成功')

    def get(self, request, good_id):
        try:
            goods = Goods.objects.get(pk=good_id)
        except Goods.DoesNotExist:
            return self.fail(message='失物信息不存在')
        return self.success(message='获取失物信息成功', data=GoodsSerializer(goods).data)

    def delete(self, request, good_id):
        try:
            Goods.objects.get(pk=good_id).delete()
        except Goods.DoesNotExist:
            return self.fail(message='失物信息不存在')
        return self.success(message='删除失物信息成功')
