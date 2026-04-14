""" Product image admin registration for the master admin site. """

from django.contrib import admin
from unfold.admin import ModelAdmin
from catalog.models import ProductImageModel
from core.adminsites.site_instances import master_admin_site


@admin.register(ProductImageModel, site=master_admin_site)
class ProductImageModelAdmin(ModelAdmin):
    """ Unfold-compatible product image admin for the master admin site. """

    list_display = ("__str__", "product", "variant", "is_primary", "sort_order", "created_at")
    list_filter = ("is_primary", "created_at")
    search_fields = ("alt_text", "image", "product__name", "variant__sku")
    autocomplete_fields = ("product", "variant")
    readonly_fields = ("created_at",)
    ordering = ("product_id", "sort_order", "id")
    list_select_related = ("product", "variant")
