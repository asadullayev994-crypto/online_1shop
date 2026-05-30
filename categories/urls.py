

from django.urls import path

from categories.views import CategoryListView, CategoryDetailView

urlpatterns = [
    path("", CategoryListView.as_view(), name="category_list"),
    path("<slug:slug>/", CategoryDetailView.as_view(), name="category_detail"),
]