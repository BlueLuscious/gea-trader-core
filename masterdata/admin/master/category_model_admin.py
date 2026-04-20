""" Category admin registration for the master admin site. """

from django.contrib import admin
from unfold.admin import ModelAdmin
from core.adminsites.site_instances import master_admin_site
from masterdata.models import CategoryModel


@admin.register(CategoryModel, site=master_admin_site)
class CategoryModelAdmin(ModelAdmin):
    """ Unfold-compatible category admin for the master admin site. """

    list_display = ("name", "parent", "is_featured", "sort_order", "is_active", "updated_at")
    list_filter = ("is_featured", "is_active", "created_at", "updated_at")
    search_fields = ("name", "slug")
    autocomplete_fields = ("parent",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("sort_order", "name")
