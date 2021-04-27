from django.urls import path
from order import views

urlpatterns = [
    path("option/", views.OrderAPIView.as_view()),
    path("option2/", views.OrderListAPIView.as_view()),
    path("option3/", views.OrderSiteAPIView.as_view()),
]
