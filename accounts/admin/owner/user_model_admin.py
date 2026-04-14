""" User admin registration for the owner admin site. """

import logging
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm
from accounts.admin.owner.tenant_membership_inline import TenantMembershipInline
from accounts.admin.owner.user_model_admin_creation_form import OwnerUserModelAdminCreationForm
from accounts.admin.owner.user_model_admin_form import OwnerUserModelAdminForm
from accounts.models import UserModel
from core.adminsites.site_instances import owner_admin_site
from tenancy.access.tenant_accounts_access_policy import TenantAccountsAccessPolicy
from tenancy.choices import TenantRole

logger = logging.getLogger(__name__)


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
    inlines = (TenantMembershipInline,)
    list_display = ("username", "email", "first_name", "last_name", "is_active", "is_staff", "last_login")
    list_filter = ("is_active", "is_staff", "date_joined")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)
    readonly_fields = ("last_login", "date_joined")

    add_fieldsets = (
        (
            _("Profile"),
            {
                "classes": ("tab",),
                "description": _("Create a team account your staff can recognize easily."),
                "fields": (
                    ("username", "email"),
                    ("first_name", "last_name"),
                    ("password1", "password2"),
                ),
            },
        ),
        (
            _("Access"),
            {
                "classes": ("tab",),
                "description": _("Control whether this account can sign in and open the business admin."),
                "fields": (("is_active", "is_staff"), "groups"),
            },
        ),
    )
    fieldsets = (
        (
            _("Profile"),
            {
                "classes": ("tab",),
                "description": _("Keep this team member's profile and contact details up to date."),
                "fields": (
                    ("username", "email"),
                    ("first_name", "last_name"),
                ),
            },
        ),
        (
            _("Access"),
            {
                "classes": ("tab",),
                "description": _("Control whether this account can sign in and open the business admin."),
                "fields": (("is_active", "is_staff"), "groups"),
            },
        ),
        (
            _("Activity"),
            {
                "classes": ("tab",),
                "description": _("Recent sign-in details for support and auditing."),
                "fields": ("last_login", "date_joined"),
            },
        ),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[UserModel]:
        """ Hide superusers and scope owner-visible users to the active tenant.

        Args:
            request: Current admin request.

        Returns:
            QuerySet[UserModel]: Owner-visible users.
        """
        queryset = super().get_queryset(request).filter(is_superuser=False)
        tenant = getattr(request, "tenant", None)

        if not TenantAccountsAccessPolicy.can_manage_accounts(request) or tenant is None:
            logger.info(
                "Returned no owner-visible users because the request cannot manage accounts tenant_id=%s",
                getattr(tenant, "pk", None),
            )
            return queryset.none()

        tenant_queryset = queryset.filter(
            tenant_memberships__tenant=tenant,
            tenant_memberships__role__in=(TenantRole.OWNER, TenantRole.OPERATOR),
        ).distinct()
        logger.info(
            "Scoped owner user queryset tenant_id=%s user_count=%s",
            tenant.pk,
            tenant_queryset.count(),
        )
        return tenant_queryset

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
            readonly_fields.extend(("is_active", "is_staff", "groups"))

        return tuple(dict.fromkeys(readonly_fields))

    def formfield_for_manytomany(self, db_field, request: HttpRequest, **kwargs):
        """ Filter assignable groups to the active tenant scope.

        Args:
            db_field: Django model field being converted into a form field.
            request: Current admin request.
            **kwargs: Remaining field construction arguments.

        Returns:
            forms.Field: Built admin form field.
        """
        if db_field.name == "groups":
            tenant = getattr(request, "tenant", None)
            if tenant is None:
                kwargs["queryset"] = Group.objects.none()
            else:
                kwargs["queryset"] = Group.objects.filter(tenant_binding__tenant=tenant).order_by("name")

        form_field = super().formfield_for_manytomany(db_field, request, **kwargs)

        if db_field.name == "groups":
            logger.info(
                "Built owner user group field tenant_id=%s group_count=%s",
                getattr(getattr(request, "tenant", None), "pk", None),
                form_field.queryset.count(),
            )

        return form_field

    def get_formset_kwargs(self, request: HttpRequest, obj, inline, prefix: str) -> dict:
        """ Inject the current request into the tenant membership inline formset.

        Args:
            request: Current admin request.
            obj: User being edited, when present.
            inline: Inline admin instance being constructed.
            prefix: Inline formset prefix.

        Returns:
            dict: Formset kwargs for the current inline.
        """
        formset_kwargs = super().get_formset_kwargs(request, obj, inline, prefix)

        if isinstance(inline, TenantMembershipInline):
            formset_kwargs["request"] = request

        return formset_kwargs

    def has_module_permission(self, request: HttpRequest) -> bool:
        """ Require an active owner membership before exposing the user module.

        Args:
            request: Current admin request.

        Returns:
            bool: ``True`` when the current user may manage accounts for the active tenant.
        """
        return TenantAccountsAccessPolicy.can_manage_accounts(request) and super().has_module_permission(request)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """ Require an active owner membership before allowing user creation.

        Args:
            request: Current admin request.

        Returns:
            bool: ``True`` when the current user may add tenant-scoped support users.
        """
        return TenantAccountsAccessPolicy.can_manage_accounts(request) and super().has_add_permission(request)

    def has_view_permission(self, request: HttpRequest, obj: UserModel | None = None) -> bool:
        """ Restrict user visibility to owner memberships for the active tenant.

        Args:
            request: Current admin request.
            obj: User being inspected, when present.

        Returns:
            bool: ``True`` when the current user may view the module and target user.
        """
        if not TenantAccountsAccessPolicy.can_manage_accounts(request):
            return False

        if not super().has_view_permission(request, obj):
            return False

        if obj is None:
            return True

        return TenantAccountsAccessPolicy.can_view_user(request, obj)

    def has_change_permission(self, request: HttpRequest, obj: UserModel | None = None) -> bool:
        """ Restrict user editing to owner memberships for the active tenant.

        Args:
            request: Current admin request.
            obj: User being edited, when present.

        Returns:
            bool: ``True`` when the current user may edit the module and target user.
        """
        if not TenantAccountsAccessPolicy.can_manage_accounts(request):
            return False

        if not super().has_change_permission(request, obj):
            return False

        if obj is None:
            return True

        return TenantAccountsAccessPolicy.can_view_user(request, obj)

    def has_delete_permission(self, request: HttpRequest, obj: UserModel | None = None) -> bool:
        """ Disable hard delete in favor of deactivation.

        Args:
            request: Current admin request.
            obj: User being edited, when present.

        Returns:
            bool: Always False for the owner flow.
        """
        return False
