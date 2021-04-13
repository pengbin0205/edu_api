from django.urls import path
from rest_framework_jwt import views
from user import views as user_view

urlpatterns = [
    # 通过jwt完成登陆
    path("login/", views.obtain_jwt_token),
    path("captcha/",user_view.CaptchaAPIView.as_view()),
]