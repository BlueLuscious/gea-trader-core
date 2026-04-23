from django.urls import path
from .views import (
    CartAddItemView,
    CartClearView,
    CartQuoteRequestView,
    CartRemoveItemView,
    CartStateView,
    CartUpdateQuantityView,
    CategoryListView,
    CategoryProductListView,
    IndexView,
    ProductDetailView,
    ProductListView,
)


urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("carrito/estado/", CartStateView.as_view(), name="cart_state"),
    path("carrito/agregar/", CartAddItemView.as_view(), name="cart_add_item"),
    path("carrito/cantidad/", CartUpdateQuantityView.as_view(), name="cart_update_quantity"),
    path("carrito/quitar/", CartRemoveItemView.as_view(), name="cart_remove_item"),
    path("carrito/vaciar/", CartClearView.as_view(), name="cart_clear"),
    path("carrito/cotizar/", CartQuoteRequestView.as_view(), name="cart_quote_request"),
    path("categorias/", CategoryListView.as_view(), name="category_list"),
    path("categorias/<slug:slug>/", CategoryProductListView.as_view(), name="category_product_list"),
    path("productos/", ProductListView.as_view(), name="product_list"),
    path("productos/<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
]
