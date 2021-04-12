from rest_framework.views import exception_handler
from django.db import DatabaseError
from rest_framework.response import Response
from rest_framework import status
from redis import RedisError
import logging

log = logging.getLogger("django")


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        view = context["view"]
        if isinstance(exc, DatabaseError) or isinstance(exc, RedisError):
            """数据库异常"""
            log.error('[%s] %s' % (view, exc))
            return Response("系统内部存储错误！", status=status.HTTP_507_INSUFFICIENT_STORAGE)

    return response