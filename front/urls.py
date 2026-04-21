from django.urls import path
from .views import (
    CategoryProductListView,
    IndexView,
    ProductDetailView,
)


urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("categorias/<slug:slug>/", CategoryProductListView.as_view(), name="category_product_list"),
    path("productos/<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
]
