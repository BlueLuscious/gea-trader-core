""" Cart admin registration for the master admin site. """

from django.contrib import admin
from unfold.admin import ModelAdmin
from cart.models import CartModel
from core.adminsites.site_instances import master_admin_site


@admin.register(CartModel, site=master_admin_site)
class CartModelAdmin(ModelAdmin):
    """ Unfold-compatible cart admin for the master admin site. """

    list_display = ("id", "user", "status", "session_key", "expires_at", "updated_at")
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("id", "session_key", "user__username", "user__email")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-updated_at", "-created_at")
    list_select_related = ("user",)
