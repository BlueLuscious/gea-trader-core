""" User admin registration for the owner admin site. """

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpRequest
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm
from accounts.admin.owner.user_model_admin_creation_form import OwnerUserModelAdminCreationForm
from accounts.admin.owner.user_model_admin_form import OwnerUserModelAdminForm
from accounts.models import UserModel
from core.adminsites.site_instances import owner_admin_site


@admin.register(UserModel, site=owner_admin_site)
class OwnerUserModelAdmin(BaseUserAdmin, ModelAdmin):
    """ Guided user admin for owner-managed support accounts. """

    class Media:
        """ Owner admin assets for small layout refinements. """

        css = {
            "all": ("accounts/admin/owner/user_model_admin.css",),
        }

    form = OwnerUserModelAdminForm
    add_form = OwnerUserModelAdminCreationForm
    change_password_form = AdminPasswordChangeForm
    save_on_top = True
    list_display = ("username", "email", "first_name", "last_name", "is_active", "is_staff", "last_login")
    list_filter = ("is_active", "is_staff", "date_joined")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)
    readonly_fields = ("last_login", "date_joined")

    add_fieldsets = (
        (
            "Profile",
            {
                "classes": ("tab",),
                "description": "Create a support account that your team can recognize easily.",
                "fields": (
                    ("username", "email"),
                    ("first_name", "last_name"),
                    ("password1", "password2"),
                ),
            },
        ),
        (
            "Access",
            {
                "classes": ("tab",),
                "description": "Control whether this account can sign in and access the owner admin.",
                "fields": (("is_active", "is_staff"),),
            },
        ),
    )
    fieldsets = (
        (
            "Profile",
            {
                "classes": ("tab",),
                "description": "Keep the support user's identity and contact details up to date.",
                "fields": (
                    ("username", "email"),
                    ("first_name", "last_name"),
                ),
            },
        ),
        (
            "Access",
            {
                "classes": ("tab",),
                "description": "Control whether this account can sign in and access the owner admin.",
                "fields": (("is_active", "is_staff"),),
            },
        ),
        (
            "Activity",
            {
                "classes": ("tab",),
                "description": "Recent sign-in information for support and auditing.",
                "fields": ("last_login", "date_joined"),
            },
        ),
    )

    def get_queryset(self, request: HttpRequest):
        """ Hide superusers from the owner admin user list.

        Args:
            request: Current admin request.

        Returns:
            QuerySet[UserModel]: Owner-visible users.
        """
        return super().get_queryset(request).filter(is_superuser=False)

    def get_readonly_fields(self, request: HttpRequest, obj: UserModel | None = None) -> tuple[str, ...]:
        """ Prevent owners from removing their own admin access by mistake.

        Args:
            request: Current admin request.
            obj: User being edited, when present.

        Returns:
            tuple[str, ...]: Read-only field names for the current screen.
        """
        readonly_fields = list(super().get_readonly_fields(request, obj))

        if obj is not None and getattr(request.user, "pk", None) == obj.pk:
            readonly_fields.extend(("is_active", "is_staff"))

        return tuple(dict.fromkeys(readonly_fields))

    def has_delete_permission(self, request: HttpRequest, obj: UserModel | None = None) -> bool:
        """ Disable hard delete in favor of deactivation.

        Args:
            request: Current admin request.
            obj: User being edited, when present.

        Returns:
            bool: Always False for the owner flow.
        """
        return False
