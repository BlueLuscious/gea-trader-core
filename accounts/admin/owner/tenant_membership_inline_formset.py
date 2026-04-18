""" Formset used by the owner user admin tenant membership inline. """

from typing import TYPE_CHECKING
import logging
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from tenancy.choices import TenantRole
from tenancy.models import TenantMembershipModel

if TYPE_CHECKING:
    from accounts.admin.owner.tenant_membership_inline_form import TenantMembershipInlineForm
    from tenancy.models.querysets.tenant_membership_model_queryset import TenantMembershipModelQuerySet

logger = logging.getLogger(__name__)


class TenantMembershipInlineFormSet(BaseInlineFormSet):
    """ Owner-scoped inline formset for one tenant membership per visible user. """

    request: HttpRequest
    can_delete = False

    def __init__(self, *args, request: HttpRequest | None = None, **kwargs) -> None:
        """ Mark the visible membership form as required in add and change flows.

        Args:
            *args: Positional formset arguments.
            request: Current admin request.
            **kwargs: Keyword formset arguments.
        """
        super().__init__(*args, **kwargs)
        self.request = request

        for form in self.forms:
            form.empty_permitted = False

    def get_queryset(self) -> "TenantMembershipModelQuerySet":
        """ Return only the membership bound to the active tenant.

        Returns:
            TenantMembershipModelQuerySet: Active-tenant membership rows for the inline.
        """
        queryset: "TenantMembershipModelQuerySet" = super().get_queryset()
        tenant = getattr(getattr(self, "request", None), "tenant", None)

        if tenant is None:
            return queryset.none()

        return queryset.filter(tenant=tenant)

    def clean(self) -> None:
        """ Require one tenant membership and preserve at least one active owner.

        Raises:
            ValidationError: When no membership is provided or the tenant would lose all active owners.
        """
        super().clean()

        if any(self.errors):
            return

        tenant = getattr(getattr(self, "request", None), "tenant", None)
        if tenant is None:
            raise ValidationError(_("This screen requires an active business in context."))

        visible_forms = [
            form
            for form in self.forms
            if getattr(form, "cleaned_data", None) and not form.cleaned_data.get("DELETE", False)
        ]

        if not visible_forms:
            raise ValidationError(_("Add one business access entry before saving this user."))

        membership_form = visible_forms[0]
        resulting_role = membership_form.cleaned_data.get("role") or TenantRole.OPERATOR
        resulting_is_active = bool(membership_form.cleaned_data.get("is_active", False))
        current_user_id = getattr(self.instance, "pk", None)
        other_active_owner_exists = (
            TenantMembershipModel.objects.for_tenant(tenant)
            .active()
            .owners()
            .exclude(user_id=current_user_id)
            .exists()
        )

        if (resulting_role != TenantRole.OWNER or not resulting_is_active) and not other_active_owner_exists:
            raise ValidationError(_("Each business must keep at least one active owner account."))

    def save_new(self, form: "TenantMembershipInlineForm", commit: bool = True) -> TenantMembershipModel:
        """ Create one membership bound to the active tenant and current user.

        Args:
            form: Bound inline form.
            commit: Whether to persist the membership immediately.

        Returns:
            TenantMembershipModel: Newly created tenant membership.
        """
        membership: TenantMembershipModel = form.save(commit=False)
        membership.user = self.instance
        membership.tenant = self.request.tenant
        membership.is_primary = False

        if commit:
            membership.save()
            form.save_m2m()
            logger.info(
                "Created tenant membership through owner inline tenant_id=%s user_id=%s role=%s is_active=%s",
                membership.tenant_id,
                membership.user_id,
                membership.role,
                membership.is_active,
            )

        return membership

    def save_existing(self, form: "TenantMembershipInlineForm", instance: TenantMembershipModel, commit: bool = True) -> TenantMembershipModel:
        """ Keep the membership anchored to the active tenant while editing it.

        Args:
            form: Bound inline form.
            instance: Membership being updated.
            commit: Whether to persist the membership immediately.

        Returns:
            TenantMembershipModel: Updated tenant membership.
        """
        membership: TenantMembershipModel = form.save(commit=False)
        membership.tenant = self.request.tenant

        if commit:
            membership.save()
            form.save_m2m()
            logger.info(
                "Updated tenant membership through owner inline tenant_id=%s user_id=%s role=%s is_active=%s",
                membership.tenant_id,
                membership.user_id,
                membership.role,
                membership.is_active,
            )

        return membership

    def save_new_objects(self, commit: bool = True) -> list[TenantMembershipModel]:
        """ Persist the visible membership form even when its values match the defaults.

        Args:
            commit: Whether to persist the memberships immediately.

        Returns:
            list[TenantMembershipModel]: Newly created memberships saved by the formset.
        """
        self.new_objects = []

        for form in self.extra_forms:
            if not getattr(form, "cleaned_data", None):
                continue

            if self.can_delete and self._should_delete_form(form):
                continue

            self.new_objects.append(self.save_new(form, commit=commit))
            if not commit:
                self.saved_forms.append(form)

        return self.new_objects
