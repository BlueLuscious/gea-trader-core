""" Tenant-membership persistence model for user access inside one business. """

from typing import TYPE_CHECKING
from uuid import UUID
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from tenancy.choices import TenantRole
from tenancy.models.managers.tenant_membership_model_manager import TenantMembershipModelManager

if TYPE_CHECKING:
    from accounts.models import UserModel
    from tenancy.models import TenantModel


class TenantMembershipModel(models.Model):
    """ Membership linking one user to one tenant with a scoped role. """

    tenant: "TenantModel" = models.ForeignKey(
        "tenancy.TenantModel",
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name=_("Business"),
        help_text=_("Business where this account receives access."),
    )
    user: "UserModel" = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tenant_memberships",
        verbose_name=_("User"),
        help_text=_("Account that receives this business access."),
    )
    role = models.CharField(
        max_length=16,
        choices=TenantRole.choices,
        default=TenantRole.OWNER,
        verbose_name=_("Business role"),
        help_text=_("Role this account will have inside the selected business."),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Access active"),
        help_text=_("Uncheck this to keep the access record without allowing day-to-day access."),
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("Primary access"),
        help_text=_("Marks this as the default business access used as a fallback context for the account."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: TenantMembershipModelManager = TenantMembershipModelManager()

    id: int
    user_id: int
    tenant_id: UUID

    class Meta:
        """ Declarative admin-facing metadata for tenant-membership persistence. """

        ordering = ("tenant__name", "user__username", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("tenant", "user"),
                name="tenant_membership_unique_tenant_user",
            ),
            models.UniqueConstraint(
                fields=("user",),
                condition=Q(is_primary=True),
                name="tenant_membership_unique_primary_per_user",
            ),
        ]
        verbose_name = _("Business access")
        verbose_name_plural = _("Business access")

    def __str__(self) -> str:
        """ Return the admin-friendly tenant membership label.

        Returns:
            str: Membership label.
        """
        return f"{self.user} -> {self.tenant} ({self.role})"
