""" Quote admin registration for the master admin site. """

from django.contrib import admin
from unfold.admin import ModelAdmin
from core.adminsites.site_instances import master_admin_site
from quotation.models import QuoteModel


@admin.register(QuoteModel, site=master_admin_site)
class QuoteModelAdmin(ModelAdmin):
    """ Unfold-compatible quote admin for the master admin site. """

    list_display = ("id", "customer_email", "workflow_status", "user", "cart", "requested_at", "updated_at")
    list_filter = ("workflow_status", "created_at", "updated_at")
    search_fields = ("=id", "customer_name", "customer_email", "company_name", "tax_id")
    autocomplete_fields = ("cart", "user")
    readonly_fields = ("requested_at", "resolved_at", "created_at", "updated_at")
    ordering = ("-created_at",)
    list_select_related = ("cart", "user")
