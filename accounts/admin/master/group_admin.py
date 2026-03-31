""" Group admin registration for the master admin site. """

from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from core.adminsites.site_instances import master_admin_site


@admin.register(Group, site=master_admin_site)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    """ Unfold-compatible group admin for the master admin site. """
