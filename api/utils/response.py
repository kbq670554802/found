from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from api.utils import status
from django.utils import six
from rest_framework.response import Response
from rest_framework.serializers import Serializer


class JsonResponse(Response):
    """
    An HttpResponse that allows its data to be rendered into
    arbitrary media types.
    """

    def __init__(self, data=None, code=status.HTTP_200_OK, msg=None,
                 status=status.HTTP_200_OK,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        """
        Alters the init arguments slightly.
        For example, drop 'template_name', and instead use 'data'.
        Setting 'renderer' and 'media_type' will typically be deferred,
        For example being set automatically by the `APIView`.
        """
        super(Response, self).__init__(None, status=status)

        if isinstance(data, Serializer):
            msg = (
                'You passed a Serializer instance as data, but '
                'probably meant to pass serialized `.data` or '
                '`.error`. representation.'
            )
            raise AssertionError(msg)

        self.data = {"code": code, "msg": msg, "data": data}
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in six.iteritems(headers):
                self[name] = value

    def paging(objs, request, serializer=None, msg=None):
        """
        objs : 实体对象
        request : 请求对象
        Serializer : 对应实体对象的序列化
        """
        try:
            page_size = int(request.GET.get('page_size', 10))
            page_index = int(request.GET.get('page_index', 1))
        except (TypeError, ValueError):
            return JsonResponse(code=status.HTTP_400_BAD_REQUEST,
                                msg='page_index和page_size必须是int!')
        paginator = Paginator(objs, page_size)  # paginator对象
        total = paginator.count
        try:
            objs_paging = paginator.page(page_index)
        except PageNotAnInteger:
            objs_paging = paginator.page(1)
        except EmptyPage:
            objs_paging = paginator.page(paginator.num_pages)

        serializer = serializer(objs_paging.object_list, many=True)
        return JsonResponse(data={
            'detail': serializer.data,
            'page_index': page_index,
            'page_size': page_size,
            'total': total,
            'has_more': objs_paging.has_next()
        }, msg=msg)  # 返回
