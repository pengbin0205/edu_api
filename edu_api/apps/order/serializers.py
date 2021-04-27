from datetime import datetime

from django.db import transaction
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from course.models import Course, CourseExpire
from order.models import Order, OrderDetail


class OrderModelSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "order_number", "pay_type")

        extra_kwargs = {
            "id": {"read_only": True},
            "order_number": {"read_only": True},
            "pay_type": {"write_only": True},

        }

    def validate(self, attrs):
        """验证前端参数"""
        pay_type = attrs.get("pay_type")
        try:
            Order.pay_choices[pay_type]
        except Order.DoesNotExist:
            raise serializers.ValidationError("您选择的支付方式不允许")

        return attrs

    def create(self, validated_data):
        """生成订单  订单详情"""

        redis_connection = get_redis_connection('cart')
        number = redis_connection.incr("number")

        # 通过request获取用户id
        user_id = self.context['request'].user.id

        # 生成唯一的订单号  时间戳 用户id  随机字符串
        order_number = datetime.now().strftime("%Y%m%d%H%M%S") + "%06d" % user_id + "%09d" % number
        print(order_number)

        with transaction.atomic():
            # 记录事务的回滚点
            savepoint = transaction.savepoint()
            # 生成订单
            order = Order.objects.create(
                order_title="百知教育在线课程订单",
                total_price=0,
                real_price=0,
                order_number=order_number,
                order_status=0,
                pay_type=validated_data.get("pay_type"),
                credit=0,
                coupon=0,
                order_desc="选择这个课程是你极其明智的决定",
                user_id=user_id,
            )

            #  从购物车中获取所有已勾选的课程
            cart_list_byte = redis_connection.hgetall("cart_%s" % user_id)
            select_list_byte = redis_connection.smembers("select_%s" % user_id)
            #  清空购物车
            select_list = redis_connection.smembers("select_%s" % user_id)
            for course2_id in select_list:
                redis_connection.hdel("cart_%s" % user_id, course2_id)
                redis_connection.srem("select_%s" % user_id, course2_id)

            for course_id_byte, expire_id_byte in cart_list_byte.items():
                course_id = int(course_id_byte)
                expire_id = int(expire_id_byte)

                if course_id_byte in select_list_byte:
                    try:
                        course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                    except Course.DoesNotExist:
                        continue

                        # 判断课程的有效期  有效期id大于0，则需要重新计算商品的价格  id不大于0代表永久有效，默认雨原价
                    original_price = course.price
                    expire_text = "永久有效"

                    try:
                        if expire_id > 0:
                            # 获取有效期的价格，再进行活动计算
                            course_expire = CourseExpire.objects.get(pk=expire_id)
                            original_price = course_expire.price
                            expire_text = course_expire.expire_text
                    except CourseExpire.DoesNotExist:
                        pass

                    # 根据已勾选的商品的价格来计算商品最终的价格
                    course_expire_price = course.expire_price(expire_id)

                    # 生成订单详情
                    try:
                        OrderDetail.objects.create(
                            order=order,
                            course=course,
                            expire=expire_id,
                            price=original_price,
                            real_price=course_expire_price,
                            discount_name=course.discount_name
                        )
                    except:
                        # 回滚
                        transaction.savepoint_rollback(savepoint)
                        raise serializers.ValidationError("订单详情生成失败")

                    # 计算订单的总价
                    order.total_price += float(original_price)
                    order.real_price += float(course_expire_price)
                order.save()

                # TODO 将已经生成订单的课程从购物车删除

            return order


class Order2ModelSerializer(ModelSerializer):
    class Meta:
        # model = Order
        # fields = ("id", "order_number", "pay_type", "order_title", "order_status1", "pay_type1", "real_price"
        #           , "total_price", "user_id", "create_time", "orderlist")
        model = Order
        fields = ("id", "order_number", "order_title", "order_status1", "pay_type1", "user_id", "orderlist"
                  ,  "create_time", "total_price", "real_price")

