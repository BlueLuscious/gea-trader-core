""" Quote item admin registration for the master admin site. """

from django.contrib import admin
from unfold.admin import ModelAdmin
from core.adminsites.site_instances import master_admin_site
from quotation.models import QuoteItemModel


@admin.register(QuoteItemModel, site=master_admin_site)
class QuoteItemModelAdmin(ModelAdmin):
    """ Unfold-compatible quote item admin for the master admin site. """

    list_display = ("id", "quote", "product_name_snapshot", "quantity", "created_at")
    list_filter = ("created_at",)
    search_fields = ("=id", "product_name_snapshot", "sku_snapshot", "=quote__id")
    autocomplete_fields = ("quote", "product", "variant")
    readonly_fields = ("created_at",)
    ordering = ("created_at", "id")
    list_select_related = ("quote", "product", "variant")
