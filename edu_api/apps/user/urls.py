from django.urls import path
from rest_framework_jwt import views
from user import views as user_view

urlpatterns = [
    # 通过jwt完成登陆
    path("login/", views.obtain_jwt_token),
    path("login2/", user_view.PhoneLoginAPIView.as_view()),
    path("captcha/",user_view.CaptchaAPIView.as_view()),
    path("register/", user_view.UserAPIView.as_view()),
    path("message/", user_view.SendMessageAPIView.as_view()),
]