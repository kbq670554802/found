from rest_framework.response import Response
from rest_framework.views import exception_handler

from api.utils import status


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['code'] = response.status_code
        response.data['msg'] = response.data['detail']
        response.status_code = status.HTTP_200_OK
        # response.data['data'] = None #可以存在
        del response.data['detail']  # 删除detail字段
    # else:
    #     response = Response(status=status.HTTP_200_OK)
    #     data = {
    #         'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         'msg': '服务器异常,请联系系统管理员!'
    #     }
    #     response.data = data
    return response
