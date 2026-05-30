

from django.urls import path

from reviews.views import (
    ProductReviewListView,
    ReviewDetailView,
    AdminReviewListView,
    AdminReviewApproveView,
)

urlpatterns = [

    path("products/<slug:slug>/", ProductReviewListView.as_view(), name="product_review_list"),
    path("<int:review_id>/", ReviewDetailView.as_view(), name="review_detail"),

  
    path("admin/", AdminReviewListView.as_view(), name="admin_review_list"),
    path("admin/<int:review_id>/approve/", AdminReviewApproveView.as_view(), name="admin_review_approve"),
    path("admin/<int:review_id>/", AdminReviewApproveView.as_view(), name="admin_review_delete"),
]