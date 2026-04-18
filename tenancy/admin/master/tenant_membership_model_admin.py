""" Tenant membership admin registration for the master admin site. """

from django.contrib import admin
from unfold.admin import ModelAdmin
from core.adminsites.site_instances import master_admin_site
from tenancy.models import TenantMembershipModel


@admin.register(TenantMembershipModel, site=master_admin_site)
class TenantMembershipModelAdmin(ModelAdmin):
    """ Unfold-compatible tenant membership admin for the master admin site. """

    list_display = ("tenant", "user", "role", "is_active", "is_primary", "updated_at")
    list_filter = ("role", "is_active", "is_primary", "created_at", "updated_at")
    search_fields = ("tenant__name", "tenant__slug", "user__username", "user__email")
    autocomplete_fields = ("tenant", "user")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("tenant__name", "user__username", "id")
    list_select_related = ("tenant", "user")
