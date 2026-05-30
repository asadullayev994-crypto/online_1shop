

from django.urls import path

from payments.views import (
    PaymentListView,
    PaymentDetailView,
    AdminPaymentListView,
    AdminPaymentUpdateView,
)

urlpatterns = [
   
    path("", PaymentListView.as_view(), name="payment_list"),
    path("<int:payment_id>/", PaymentDetailView.as_view(), name="payment_detail"),

  
    path("admin/", AdminPaymentListView.as_view(), name="admin_payment_list"),
    path("admin/<int:payment_id>/", AdminPaymentUpdateView.as_view(), name="admin_payment_update"),
]