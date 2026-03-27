""" Product admin registration for the master admin site. """

from django.contrib import admin
from unfold.admin import ModelAdmin
from catalog.models import ProductModel
from core.adminsites.site_instances import master_admin_site


@admin.register(ProductModel, site=master_admin_site)
class ProductModelAdmin(ModelAdmin):
    """ Unfold-compatible product admin for the master admin site. """

    list_display = (
        "name",
        "brand",
        "category",
        "is_active",
        "is_featured",
        "requires_quote",
        "updated_at",
    )
    list_filter = ("is_active", "is_featured", "requires_quote", "brand", "category")
    search_fields = ("name", "slug", "sku_base")
    autocomplete_fields = ("brand", "category")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)
    list_select_related = ("brand", "category")
