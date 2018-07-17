from django import forms

from account.models import User
from announce.models import Goods, PageInfo
from ._serializers import serializers, UsernameSerializer


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(UserLoginSerializer, self).__init__(*args, **kwargs)
        self.fields['password'].error_messages['required'] = u'请输入密码！'


class UsernameOrEmailCheckSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=32)
    password = serializers.CharField(min_length=6)
    email = serializers.EmailField(max_length=64)
    captcha = serializers.CharField()


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=6)
    tfa_code = serializers.CharField(required=False, allow_blank=True)


class UserChangeEmailSerializer(serializers.Serializer):
    password = serializers.CharField()
    new_email = serializers.EmailField(max_length=64)
    tfa_code = serializers.CharField(required=False, allow_blank=True)


class GenerateUserSerializer(serializers.Serializer):
    prefix = serializers.CharField(max_length=16, allow_blank=True)
    suffix = serializers.CharField(max_length=16, allow_blank=True)
    number_from = serializers.IntegerField()
    number_to = serializers.IntegerField()
    password_length = serializers.IntegerField(max_value=16, default=8)


class ImportUserSeralizer(serializers.Serializer):
    users = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField(max_length=64)))


# 用户信息序列化
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'real_name', 'avatar', 'birth')


# 失物信息序列化
class GoodsSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    name = serializers.CharField(required=True, min_length=2, max_length=20,
                                 error_messages={
                                     'required': '请填写名字',
                                     'blank': '请填写名字',
                                     'min_length': '名字不能小于2个字符',
                                     'max_length': '名字不能大于20个字符',
                                 })
    phone = serializers.CharField(required=False, min_length=12, max_length=12,
                                  error_messages={
                                      'required': '请输入手机号',
                                      'blank': '请输入手机号',
                                      'min_length': '请输入合法手机号',
                                      'max_length': '请输入合法手机号',
                                  })
    contact = serializers.CharField(required=False, allow_blank=True, max_length=100,
                                    error_messages={
                                        'max_length': '其他联系方式不得超过100字',
                                    })
    lost_date = serializers.DateTimeField(required=True,
                                          error_messages={
                                              'required': '请输入遗失时间',
                                              'blank': '请输入遗失时间',
                                          })
    lost_addr = serializers.CharField(required=True, max_length=100,
                                      error_messages={
                                          'required': '请输入遗失地点',
                                          'max_length': '遗失地点不得超过100字',
                                      })
    summary = serializers.CharField(required=True, max_length=100,
                                    error_messages={
                                        'required': '请输入概要',
                                        'max_length': '概要不得超过100字',
                                    })
    content = serializers.CharField(required=False, max_length=1000,
                                    error_messages={
                                        'max_length': '详细描述不得超过1000字',
                                    })

    class Meta:
        model = Goods
        fields = ('name', 'phone', 'contact', 'lost_date', 'lost_addr', 'summary', 'user', 'create_time', 'content')

    def __init__(self, *args, **kwargs):
        super(GoodsSerializer, self).__init__(*args, **kwargs)
        self.fields['name'].error_messages['max_length'] = u'长度！'
        self.fields['name'].error_messages['blank', 'required'] = u'请输入姓名！'


# 失物增/改信息序列化
class GoodsEditValidate(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=True, min_length=2, max_length=20,
                                 error_messages={
                                     'required': '请填写名字',
                                     'blank': '请填写名字',
                                     'min_length': '名字不能小于2个字符',
                                     'max_length': '名字不能大于20个字符',
                                 })
    phone = serializers.CharField(required=False, min_length=11, max_length=11,
                                  error_messages={
                                      'required': '请输入手机号',
                                      'blank': '请输入手机号',
                                      'min_length': '请输入合法手机号',
                                      'max_length': '请输入合法手机号',
                                  })
    contact = serializers.CharField(required=False, allow_blank=True, max_length=100,
                                    error_messages={
                                        'max_length': '其他联系方式不得超过100字',
                                    })
    lost_date = serializers.DateField(required=True,
                                      error_messages={
                                          'required': '请输入遗失时间',
                                          'blank': '请输入遗失时间',
                                      })
    lost_addr = serializers.CharField(required=True, max_length=100,
                                      error_messages={
                                          'required': '请输入遗失地点',
                                          'blank': '请输入遗失地点',
                                          'max_length': '遗失地点不得超过100字',
                                      })
    summary = serializers.CharField(required=True, max_length=100,
                                    error_messages={
                                        'required': '请输入概要',
                                        'blank': '请输入概要',
                                        'max_length': '概要不得超过100字',
                                    })
    content = serializers.CharField(required=False, allow_blank=True, max_length=1000,
                                    error_messages={
                                        'max_length': '详细描述不得超过1000字',
                                    })

    class Meta:
        model = Goods
        fields = (
            'id', 'type', 'name', 'phone', 'contact', 'lost_date', 'lost_addr', 'summary', 'user', 'create_time',
            'content')


# 失物信息序列化
class GoodsListSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Goods
        fields = ('id', 'name', 'phone', 'contact', 'lost_date', 'lost_addr', 'summary', 'user', 'create_time')


# 分页信息校验
class PaginatorBaseSerializer(serializers.Serializer):
    page_index = serializers.IntegerField(required=True, min_value=1,
                                          error_messages={
                                              'required': '请指定当前页',
                                              'min_value': '当前页必须大于0',
                                          })
    page_size = serializers.IntegerField(required=True, min_value=1,
                                         error_messages={
                                             'required': '请指定每页大小',
                                             'min_value': '每页大小必须大于0',
                                         })
