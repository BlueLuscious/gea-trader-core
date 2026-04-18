""" Tenant-group admin registration for the master admin site. """

from django.contrib import admin
from unfold.admin import ModelAdmin
from core.adminsites.site_instances import master_admin_site
from tenancy.models import TenantGroupModel


@admin.register(TenantGroupModel, site=master_admin_site)
class TenantGroupModelAdmin(ModelAdmin):
    """ Unfold-compatible tenant-group admin for the master admin site. """

    list_display = ("tenant", "group", "updated_at")
    search_fields = ("tenant__name", "tenant__slug", "group__name")
    autocomplete_fields = ("tenant", "group")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("tenant__name", "group__name", "id")
    list_select_related = ("tenant", "group")
