""" User admin registration for the master admin site. """

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from accounts.models import UserModel
from core.adminsites.site_instances import master_admin_site


@admin.register(UserModel, site=master_admin_site)
class UserModelAdmin(BaseUserAdmin, ModelAdmin):
    """ Unfold-compatible user admin for the master admin site. """

    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
