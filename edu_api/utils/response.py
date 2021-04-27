from rest_framework.response import Response

# Response封装
class APIResponse(Response):

    def __init__(self, data_status=200, data_message=0, results=None,
                 http_status=None, headers=None, exception=False, **kwargs):
        # 定义数据返回的状态
        data = {
            "status": data_status,
            "message": data_message,
        }

        # 判断result是否有结果
        if results is not None:
            data['results'] = results

        # 如果还需要传递自定义参数 使用可变长参数kwargs接收
        # 如果可变长参数有值，则更新到data中  反之不做任何改变
        data.update(kwargs)

        # 获取一个Response对象  将自定义的Response对象响应回去
        super().__init__(data=data, status=http_status, headers=headers, exception=exception)
