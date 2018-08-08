from django import forms

from account.models import User
from announce.models import Goods, PageInfo
from ._serializers import serializers, UsernameSerializer


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
class GoodsDetailSerializer(serializers.ModelSerializer):
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
