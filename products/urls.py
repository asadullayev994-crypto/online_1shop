

from django.urls import path

from products.views import (
    ProductListView,
    ProductDetailView,
    ProductImageView,
    MyProductsView,
)

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("my/", MyProductsView.as_view(), name="my_products"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
    path("<slug:slug>/images/", ProductImageView.as_view(), name="product_image_add"),
    path("<slug:slug>/images/<int:image_id>/", ProductImageView.as_view(), name="product_image_delete"),
]