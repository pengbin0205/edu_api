from django.urls import path

from home import views

urlpatterns = [
    path("banner/", views.BannerListView.as_view()),
    path("header/", views.HeaderListView.as_view()),
    path("footer/", views.FooterListView.as_view()),
]