import time

from edu_api.settings.constants import TIME
from my_task.main import app
from order.models import OrderDetail, Order


@app.task(name="check_order")
def check_order():
    order = Order.objects.all()
    for value in order:
        create_time = value.create_time.timestamp()
        status = value.order_status
        order_number = value.order_number
        now_time = time.time()
        if now_time - create_time >= TIME and status == 0:
            try:
                order_change = Order.objects.get(order_number=order_number,)
                order_change.order_status = 3
                order_change.save()
            except:
                return False
    return True
