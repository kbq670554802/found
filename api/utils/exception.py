import copy

from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler

from api.utils import status


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        data = copy.copy(response.data)
        response.data['code'] = response.status_code
        response.status_code = status.HTTP_200_OK
        # response.data['data'] = None
        if data:
            if isinstance(exc, ValidationError):  # 表单校验失败
                values = list(data.values())
                response.data['msg'] = values[0][0]
                for key in data.keys():
                    del response.data[key]
            else:  # 普通错误,如验证失败
                response.data['msg'] = data.get('detail')
                del response.data['detail']  # 删除detail字段
    # else:
    #     response = Response(status=status.HTTP_200_OK)
    #     data = {
    #         'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         'msg': '服务器异常,请联系系统管理员!'
    #     }
    #     response.data = data
    return response
