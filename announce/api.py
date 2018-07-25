import functools
import json
import logging
from collections import OrderedDict

from django.http import HttpResponse, QueryDict
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from rest_framework.views import APIView

logger = logging.getLogger("")


class ContentType(object):
    json_request = "application/json"
    json_response = "application/json;charset=UTF-8"
    url_encoded_request = "application/x-www-form-urlencoded"
    binary_response = "application/octet-stream"


class APIError(Exception):
    def __init__(self, msg, err=None):
        self.err = err
        self.msg = msg
        super().__init__(err, msg)


class JSONParser(object):
    content_type = ContentType.json_request

    @staticmethod
    def parse(body):
        return json.loads(body.decode("utf-8"))


class URLEncodedParser(object):
    content_type = ContentType.url_encoded_request

    @staticmethod
    def parse(body):
        return QueryDict(body)


class JSONResponse(object):
    content_type = ContentType.json_response

    @classmethod
    def response(cls, data):
        resp = HttpResponse(json.dumps(data, indent=4), content_type=cls.content_type)
        resp.data = data
        return resp


class APIView(APIView):
    """
    Django view的父类, 和django-rest-framework的用法基本一致
     - request.data获取解析之后的json或者urlencoded数据, dict类型
     - self.success, self.error和self.invalid_serializer可以根据业需求修改,
        写到父类中是为了不同的人开发写法统一,不再使用自己的success/error格式
     - self.response 返回一个django HttpResponse, 具体在self.response_class中实现
     - parse请求的类需要定义在request_parser中, 目前只支持json和urlencoded的类型, 用来解析请求的数据
    """
    request_parsers = (JSONParser, URLEncodedParser)
    response_class = JSONResponse

    def _get_request_data(self, request):
        if request.method not in ["GET", "DELETE"]:
            body = request.body
            content_type = request.META.get("CONTENT_TYPE")
            if not content_type:
                raise ValueError("content_type is required")
            for parser in self.request_parsers:
                if content_type.startswith(parser.content_type):
                    break
            # else means the for loop is not interrupted by break
            else:
                raise ValueError("unknown content_type '%s'" % content_type)
            if body:
                return parser.parse(body)
            return {}
        return request.GET

    def response(self, data):
        return self.response_class.response(data)

    def success(self, code=0, msg=None, data=None):
        return self.response({'code': code, "error": None, 'msg': msg, "data": data})

    def fail(self, code=-1, msg=None, err="error", data=None):
        return self.response({'code': code, 'msg': msg, "error": err, "data": data})

    def error(self, code=-2, msg="error", err="error"):
        return self.response({'code': code, "error": err, 'msg': msg, "data": None})

    def _serializer_error_to_str(self, errors):
        for k, v in errors.items():
            if isinstance(v, list):
                return k, v[0]
            elif isinstance(v, OrderedDict):
                for _k, _v in v.items():
                    return self._serializer_error_to_str({_k: _v})

    def invalid_serializer(self, serializer):
        k, v = self._serializer_error_to_str(serializer.errors)
        if k != "non_field_errors":
            return self.error(err="invalid:" + k + ", " + v, msg=v)
        else:
            return self.error(err="invalid-field", msg=v)

    def server_error(self):
        return self.error(err="server-error", msg="server error")

    def paginate_data(self, request, query_set, object_serializer=None):
        """
        :param request: django的request
        :param query_set: django model的query set或者其他list like objects
        :param object_serializer: 用来序列化query set, 如果为None, 则直接对query set切片
        :return:
        """
        try:
            limit = int(request.GET.get("limit", "10"))
        except ValueError:
            limit = 10
        if limit < 0 or limit > 250:
            limit = 10
        try:
            offset = int(request.GET.get("offset", "0"))
        except ValueError:
            offset = 0
        if offset < 0:
            offset = 0
        results = query_set[offset:offset + limit]
        if object_serializer:
            count = query_set.count()
            results = object_serializer(results, many=True).data
        else:
            count = query_set.count()
        data = {"results": results,
                "total": count}
        return data

    def dispatch(self, request, *args, **kwargs):
        if self.request_parsers:
            try:
                request.data = self._get_request_data(self.request)
            except ValueError as e:
                return self.error(err="invalid-request", msg=str(e))
        try:
            return super(APIView, self).dispatch(request, *args, **kwargs)
        except APIError as e:
            ret = {"msg": e.msg}
            if e.err:
                ret["err"] = e.err
            return self.error(**ret)
        except Exception as e:
            logger.exception(e)
            return self.server_error()

    def result_list(self, result_list=None, page_size=0, page_index=0, page_count=0, total_count=0, has_more=False):
        data = {
            'result': result_list,
            'page_size': page_size,
            'page_index': page_index,
            'page_count': page_count,
            'total_count': total_count,
            'has_more': has_more
        }
        return data


class CSRFExemptAPIView(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CSRFExemptAPIView, self).dispatch(request, *args, **kwargs)


def validate_serializer(serializer):
    """
    @validate_serializer(TestSerializer)
    def post(self, request):
        return self.success(request.data)
    """

    def validate(view_method):
        @functools.wraps(view_method)
        def handle(*args, **kwargs):
            self = args[0]
            request = args[1]
            s = serializer(data=request.data)
            if s.is_valid():
                request.data = s.data
                request.serializer = s
                return view_method(*args, **kwargs)
            else:
                return self.invalid_serializer(s)

        return handle

    return validate
