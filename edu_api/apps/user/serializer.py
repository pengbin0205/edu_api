import re

from django.contrib.auth.hashers import make_password
from rest_framework.serializers import ModelSerializer


from user.models import UserInfo
from rest_framework import serializers

from user.utils import get_user_by_account


class UserModelSerializer(ModelSerializer):
    sms_code = serializers.CharField(max_length=6, min_length=4, required=True, write_only=True)
    # 自定义字段 模型里没有
    token = serializers.CharField(max_length=1024, read_only=True, help_text="返回前端token")

    # 模型里有 需要匹配
    class Meta:
        model = UserInfo
        fields= ("phone", "password", "id", "username", "token", "sms_code")

        extra_kwargs = {
            "phone" :{
                "write_only" : True,
            },
            "password": {
                "write_only": True,
            },
            "id": {
                "read_only": True,
            },
            "username": {
                "read_only": True,
            },
        }

    def validate(self, attrs):
        """验证用户提交的注册信息是否合法"""
        phone = attrs.get("phone")
        password = attrs.get("password")
        code = attrs.get("sms_code")

        #验证手机号的格式
        if not re.match(r'^1[356789]\d{9}$', phone):
            raise serializers.ValidationError("手机号格式有误")

        # 手机号是否被注册
        try:
            user=get_user_by_account(account=phone)
        except:
            user = None
        if user:
            return serializers.ValidationError("当前手机号已经被注册")


        #验证密码
        if not re.match(r'^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,16}$', password):
            raise serializers.ValidationError("密码格式有误")

        from django_redis import get_redis_connection
        connection = get_redis_connection("sms_code")
        redis_code = connection.get(f"mobile_{phone}")
        if redis_code.decode() != code:
            raise serializers.ValidationError("验证码不正确")


        return attrs



    def create(self, validated_data):
        """重写create方法 完成对象的保存 token生成"""

        phone= validated_data.get("phone")
        password = validated_data.get("password")

        # 用户名处理 设置默认用户名 与 密码加密
        username = phone
        hash_pwd = make_password(password)

        #创建对象 保存对象
        user=UserInfo.objects.create(
            phone = phone,
            username = username,
            password = hash_pwd
        )

        # 用户创建后为该用户生成token
        if user:
            from rest_framework_jwt.settings import api_settings
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            user.token = jwt_encode_handler(payload)

        return user









