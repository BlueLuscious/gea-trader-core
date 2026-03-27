""" Brand admin registration for the master admin site. """

from django.contrib import admin
from unfold.admin import ModelAdmin
from core.adminsites.site_instances import master_admin_site
from masterdata.models import BrandModel


@admin.register(BrandModel, site=master_admin_site)
class BrandModelAdmin(ModelAdmin):
    """ Unfold-compatible brand admin for the master admin site. """

    list_display = ("name", "slug", "is_active", "updated_at")
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("name", "slug")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)
