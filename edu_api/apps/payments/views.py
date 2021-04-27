from datetime import datetime

from alipay import AliPay
from django.conf import settings
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

from course.models import CourseExpire
from order.models import Order
from payments.models import UserCourse



class ALiPayAPIView(APIView):

    def get(self, request):
        """生成支付宝支付的链接"""
        order_number = request.query_params.get("order_number")
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return Response({"message": "对不起，您支付的订单不存在"}, status=status.HTTP_400_BAD_REQUEST)

        # 初始化支付参数
        alipay = AliPay(
            appid=settings.ALIAPY_CONFIG['appid'],
            app_notify_url=settings.ALIAPY_CONFIG['app_notify_url'],  # 默认回调url
            app_private_key_string=settings.ALIAPY_CONFIG['app_private_key_path'],
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=settings.ALIAPY_CONFIG['alipay_public_key_path'],
            sign_type=settings.ALIAPY_CONFIG['sign_type'],  # RSA 或者 RSA2
            debug=settings.ALIAPY_CONFIG['debug'],  # 默认False
        )

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            # 订单号
            out_trade_no=order.order_number,
            total_amount=float(order.real_price),
            subject=order.order_title,
            return_url=settings.ALIAPY_CONFIG['return_url'],
            notify_url=settings.ALIAPY_CONFIG['notify_url'],  # 可选, 不填则使用默认notify url
        )

        url = settings.ALIAPY_CONFIG['gateway_url'] + order_string

        return Response(url)


class PayResultAPIView(APIView):
    """支付成功后的结果处理"""

    def get(self, request):
        alipay = AliPay(
            appid=settings.ALIAPY_CONFIG['appid'],
            app_notify_url=settings.ALIAPY_CONFIG['app_notify_url'],  # 默认回调url
            app_private_key_string=settings.ALIAPY_CONFIG['app_private_key_path'],
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=settings.ALIAPY_CONFIG['alipay_public_key_path'],
            sign_type=settings.ALIAPY_CONFIG['sign_type'],  # RSA 或者 RSA2
            debug=settings.ALIAPY_CONFIG['debug'],  # 默认False
        )

        # 验证支付的异步通知
        data = request.query_params.dict()

        signature = data.pop("sign")

        verify = alipay.verify(data, signature)
        print(verify)

        if verify:
            # 处理订单状态，生成用户购买记录，返回支付成功的结果
            return self.order_result_pay(data)

        return Response({"message": "对不起，支付失败"})

    def order_result_pay(self, data):
        """处理订单状态，生成用户购买记录，返回支付成功的结果"""
        order_number = data.get("out_trade_no")


        try:
            order = Order.objects.get(order_number=order_number, order_status=0)
        except Order.DoesNotExist:
            return Response({"message": "订单有问题~"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            savepoint = transaction.savepoint()

            # 修改订单状态
            try:
                order.pay_time = datetime.now()
                order.order_status = 1
                order.save()

                # 获取用户
                user = order.user
                # 获取用户购买当前订单的课程
                order_courses_all = order.order_courses.all()
                # 订单结算页所展示的信息
                course_list = []

                for order_detail in order_courses_all:
                    """遍历本次订单中购买的所有课程"""
                    course = order_detail.course
                    course.students += 1
                    course.save()

                    # 判断用户购买的课程是否是永久
                    pay_time_timestamp = order.pay_time.timestamp()

                    # 如果不是永久课程
                    if order_detail.expire > 0:
                        expire = CourseExpire.objects.get(pk=order_detail.expire)
                        expire_time = expire.expire_time * 24 * 60 * 60
                        # 当前时间+购买时间=到期时间
                        end_time = datetime.fromtimestamp(pay_time_timestamp + expire_time)
                    else:
                        # 永久有效
                        end_time = None

                    # 为用户生成购买记录
                    UserCourse.objects.create(
                        user=user,
                        course=order_detail.course,
                        trade_no=data.get("trade_no"),
                        buy_type=1,
                        pay_time=order.pay_time,
                        out_time=end_time,
                        orders=0,
                    )
                    # 将页面所需的课程信息存放到course_list
                    course_list.append({
                        "id": order_detail.course.id,
                        "name": order_detail.course.name,
                    })
            except:
                transaction.savepoint_rollback(savepoint)
                return Response({"message": "对不起，信息更新失败"})

            # 返回页面所需的信息
            return Response({
                "order_number": order.order_number,
                "pay_time": order.pay_time,
                "real_price": order.real_price,
                "course_list": course_list,
            })


class SiteAPIView(APIView):

    def post(self, request):
        site = request.data.get("site")
        print(site)
        order_number = request.data.get("order_number")
        print(order_number)
        connection = get_redis_connection("sms_code")
        connection.setex(f"site_{order_number}", 1800, site)

        return Response("OK")