""" Inline used by the owner user admin for tenant memberships. """

from typing import TYPE_CHECKING
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from accounts.access import AccountsAccessPolicy
from unfold.admin import TabularInline
from accounts.admin.owner.tenant_membership_inline_form import TenantMembershipInlineForm
from accounts.admin.owner.tenant_membership_inline_formset import TenantMembershipInlineFormSet
from tenancy.models import TenantMembershipModel

if TYPE_CHECKING:
    from accounts.models.user_model import UserModel
    from tenancy.models.querysets.tenant_membership_model_queryset import TenantMembershipModelQuerySet


class TenantMembershipInline(TabularInline):
    """ Edit only the active-tenant membership for the current owner user screen. """

    model = TenantMembershipModel
    form = TenantMembershipInlineForm
    formset = TenantMembershipInlineFormSet
    tab = True
    min_num = 1
    max_num = 1
    can_delete = False
    fields = ("role", "is_active")
    verbose_name = _("Business access")
    verbose_name_plural = _("Business access")

    def has_view_permission(self, request: HttpRequest, obj=None) -> bool:
        """ Allow the inline when the current user may manage the active tenant.

        Args:
            request: Current admin request.
            obj: Parent user being edited, when present.

        Returns:
            bool: ``True`` when the current user may view the tenant membership inline.
        """
        return AccountsAccessPolicy.can_manage_accounts(request)

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        """ Allow inline edits when the current user may manage the active tenant.

        Args:
            request: Current admin request.
            obj: Parent user being edited, when present.

        Returns:
            bool: ``True`` when the current user may change the tenant membership inline.
        """
        return AccountsAccessPolicy.can_manage_accounts(request)

    def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
        """ Allow inline adds when the current user may manage the active tenant.

        Args:
            request: Current admin request.
            obj: Parent user being edited, when present.

        Returns:
            bool: ``True`` when the current user may add the tenant membership inline.
        """
        return AccountsAccessPolicy.can_manage_accounts(request)

    def get_queryset(self, request: HttpRequest) -> "TenantMembershipModelQuerySet":
        """ Return only memberships that belong to the active tenant.

        Args:
            request: Current admin request.

        Returns:
            TenantMembershipModelQuerySet: Active-tenant memberships for the inline.
        """
        queryset = super().get_queryset(request)
        tenant = getattr(request, "tenant", None)

        if tenant is None:
            return queryset.none()

        return queryset.filter(tenant=tenant)
    
    def get_readonly_fields(self, request: HttpRequest, obj: "UserModel | None" = None) -> tuple[str, ...]:
        """ Prevent owners from removing their own admin access by mistake.

        Args:
            request: Current admin request.
            obj: User being edited, when present.

        Returns:
            tuple[str, ...]: Read-only field names for the current screen.
        """
        readonly_fields = list(super().get_readonly_fields(request, obj))

        if obj is not None and getattr(request.user, "pk", None) == obj.pk:
            readonly_fields.extend(("role", "is_active"))

        return tuple(dict.fromkeys(readonly_fields))
