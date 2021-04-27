from django.urls import path

from cart import views

urlpatterns = [
    path("option/", views.CartView.as_view({'post': 'add_cart', "get": "list_cart", "patch": "change_cart_select", "delete": "del_item_select"})),
    path("option2/", views.CartView.as_view({"patch": "expire_item_select","post": "get_cart_length"})),
    path("order/", views.CartView.as_view({"get": "get_select_course"})),
]