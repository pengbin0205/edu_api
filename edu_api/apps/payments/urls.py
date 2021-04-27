from django.urls import path
from payments import views

urlpatterns = [
    path("pay/", views.ALiPayAPIView.as_view()),
    path("results/", views.PayResultAPIView.as_view()),
    path("site/", views.SiteAPIView.as_view()),
]
