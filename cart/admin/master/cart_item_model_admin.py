""" Cart item admin registration for the master admin site. """

from django.contrib import admin
from unfold.admin import ModelAdmin
from cart.models import CartItemModel
from core.adminsites.site_instances import master_admin_site


@admin.register(CartItemModel, site=master_admin_site)
class CartItemModelAdmin(ModelAdmin):
    """ Unfold-compatible cart item admin for the master admin site. """

    list_display = ("id", "cart", "product", "variant", "quantity", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("=id", "=cart__id", "product__name", "variant__sku")
    autocomplete_fields = ("cart", "product", "variant")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("created_at", "id")
    list_select_related = ("cart", "product", "variant")
