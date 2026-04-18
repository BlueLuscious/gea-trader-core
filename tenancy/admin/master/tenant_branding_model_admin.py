""" Tenant-branding admin registration for the master admin site. """

from django.contrib import admin
from unfold.admin import ModelAdmin
from core.adminsites.site_instances import master_admin_site
from tenancy.models import TenantBrandingModel


@admin.register(TenantBrandingModel, site=master_admin_site)
class TenantBrandingModelAdmin(ModelAdmin):
    """ Unfold-compatible tenant-branding admin for the master admin site. """

    list_display = ("tenant", "display_name", "updated_at")
    search_fields = ("tenant__name", "tenant__slug", "display_name")
    autocomplete_fields = ("tenant",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("tenant__name", "id")
    list_select_related = ("tenant",)
