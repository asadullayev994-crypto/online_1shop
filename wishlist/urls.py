

from django.urls import path

from wishlist.views import (
    WishlistView,
    WishlistItemAddView,
    WishlistItemDeleteView,
)

urlpatterns = [
    path("", WishlistView.as_view(), name="wishlist"),
    path("add/", WishlistItemAddView.as_view(), name="wishlist_item_add"),
    path("items/<int:item_id>/", WishlistItemDeleteView.as_view(), name="wishlist_item_delete"),
]