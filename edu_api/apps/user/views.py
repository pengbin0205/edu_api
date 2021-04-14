# from urllib import request
import random

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status as http_status

from edu_api.libs.geetest import GeetestLib
from edu_api.settings import constants
from edu_api.utils.message import Message
from user.models import UserInfo
from user.serializer import UserModelSerializer
from user.utils import get_user_by_account
from django_redis import get_redis_connection

pc_geetest_id = "eceb3f15b58977f4ccbf2680069aa19d"
pc_geetest_key = "2193c33833d27bf218e80d400618f525"


class CaptchaAPIView(APIView):
    """
    极验验证码视图类
    """
    user_id = 0
    status = False

    def get(self, request):
        """获取验证码方法"""

        account = request.query_params.get('account')
        # 根据前端输入的账号来获取对应的用户
        user = get_user_by_account(account)

        if user is None:
            return Response({"msg": "用户不存在"}, status=http_status.HTTP_400_BAD_REQUEST)

        self.user_id = user.id
        # 构建一个验证码对象
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        self.status = gt.pre_process(self.user_id)
        # 响应获取的数据
        response_str = gt.get_response_str()
        return Response(response_str)

    def post(self, request):
        """比对验证码的方法"""
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.data.get(gt.FN_CHALLENGE, '')
        validate = request.data.get(gt.FN_VALIDATE, '')
        seccode = request.data.get(gt.FN_SECCODE, '')
        account = request.data.get("account")
        user = get_user_by_account(account)

        if user:
            result = gt.success_validate(challenge, validate, seccode, user.id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        result = {"status": "success"} if result else {"status": "fail"}
        return Response(result)

class UserAPIView(CreateAPIView):
    """用户视图"""
    queryset = UserInfo.objects.all()
    serializer_class = UserModelSerializer


class SendMessageAPIView(APIView):
    """短信验证码"""
    def get(self, request):
        # 获取 redis链接
        redis_connection =  get_redis_connection("sms_code")

        #1. 判断该手机格式以及是否60s内发送过验证码
        redis_connection.get("sms_code")
        phone = request.query_params.get("phone")

        #2. 生成随机验证码
        phone_code = redis_connection.get("sms_%s" % phone)
        print(phone_code)
        if phone_code:
            return Response({"message": "您已经在60s内发送过验证码了"}, status=http_status.HTTP_400_BAD_REQUEST)
        code = "%06d" % random.randint(0,999999)

        #3. 将验证码保存到redis中
        redis_connection.setex("sms_%s" % phone, constants.SMS_EXPIRE_TIME, code)
        redis_connection.setex("mobile_%s" % phone, constants.MOBILE_EXPIRE_TIME, code)


        #4. 调用发送短信方法，完成发送
        message = Message("40d6180426417bfc57d0744a362dc108")
        status = message.send_message(phone, code)

        #5. 响应发送的结果
        return Response({"message": "发送短信成功"})