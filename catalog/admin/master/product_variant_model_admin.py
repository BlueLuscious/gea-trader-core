""" Product variant admin registration for the master admin site. """

from django.contrib import admin
from unfold.admin import ModelAdmin
from catalog.models import ProductVariantModel
from core.adminsites.site_instances import master_admin_site


@admin.register(ProductVariantModel, site=master_admin_site)
class ProductVariantModelAdmin(ModelAdmin):
    """ Unfold-compatible product variant admin for the master admin site. """

    list_display = ("sku", "product", "name", "is_default", "is_active", "sort_order", "updated_at")
    list_filter = ("is_default", "is_active", "created_at", "updated_at")
    search_fields = ("sku", "name", "product__name")
    autocomplete_fields = ("product",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("product_id", "sort_order", "name", "id")
    list_select_related = ("product",)
