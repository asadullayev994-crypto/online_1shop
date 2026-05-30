

from django.urls import path

from orders.views import (
    OrderListView,
    OrderDetailView,
    OrderCancelView,
    AdminOrderListView,
    AdminOrderUpdateView,
)

urlpatterns = [
  
    path("", OrderListView.as_view(), name="order_list"),
    path("<int:order_id>/", OrderDetailView.as_view(), name="order_detail"),
    path("<int:order_id>/cancel/", OrderCancelView.as_view(), name="order_cancel"),

    
    path("admin/", AdminOrderListView.as_view(), name="admin_order_list"),
    path("admin/<int:order_id>/", AdminOrderUpdateView.as_view(), name="admin_order_update"),
]