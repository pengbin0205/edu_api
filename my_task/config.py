
from my_task.main import app

# 任务队列的链接地址
broker_url = "redis://192.168.37.130:6379/11"
# 结果队列的链接地址
result_backend = "redis://192.168.37.130:6379/12"
# 定时任务调度
app.conf.beat_schedule = {
    'check_order_status': {
        # 指定定时执行的哪个任务  直接写任务名
        'task': 'check_order',
        # 定时任务执行的周期
        'schedule': 30.0,
        # 定时任务所需参数 有参数就传递
        # 'args': (16, 16)
    },
}

# celery -A my_task.main beat
# celery -A my_task.main worker --loglevel=info