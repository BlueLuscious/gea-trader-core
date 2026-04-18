""" Reusable queryset helpers for the tenant membership model. """

from typing import TYPE_CHECKING
from django.db import models
from tenancy.choices import TenantRole

if TYPE_CHECKING:
    from accounts.models import UserModel
    from tenancy.models import TenantMembershipModel, TenantModel


class TenantMembershipModelQuerySet(models.QuerySet["TenantMembershipModel"]):
    """ QuerySet for reusable tenant membership filters. """

    def active(self) -> "TenantMembershipModelQuerySet":
        """ Filter memberships that remain active.

        Returns:
            TenantMembershipModelQuerySet: Active memberships only.
        """
        return self.filter(is_active=True)

    def for_user(self, user: "UserModel") -> "TenantMembershipModelQuerySet":
        """ Filter memberships belonging to one user.

        Args:
            user: User whose memberships should be returned.

        Returns:
            TenantMembershipModelQuerySet: Memberships linked to the provided user.
        """
        return self.filter(user=user)

    def for_tenant(self, tenant: "TenantModel") -> "TenantMembershipModelQuerySet":
        """ Filter memberships belonging to one tenant.

        Args:
            tenant: Tenant whose memberships should be returned.

        Returns:
            TenantMembershipModelQuerySet: Memberships linked to the provided tenant.
        """
        return self.filter(tenant=tenant)

    def with_tenant(self) -> "TenantMembershipModelQuerySet":
        """ Eager-load the related tenant for membership reads.

        Returns:
            TenantMembershipModelQuerySet: Memberships with ``tenant`` selected.
        """
        return self.select_related("tenant")

    def for_active_tenant(self) -> "TenantMembershipModelQuerySet":
        """ Filter memberships whose tenant remains active.

        Returns:
            TenantMembershipModelQuerySet: Memberships linked to active tenants.
        """
        return self.filter(tenant__is_active=True)

    def for_user_active_tenants(self, user: "UserModel") -> "TenantMembershipModelQuerySet":
        """ Return active memberships for one user across active tenants.

        Args:
            user: User whose active tenant memberships should be returned.

        Returns:
            TenantMembershipModelQuerySet: Active memberships for active tenants.
        """
        return self.active().for_user(user).for_active_tenant()

    def ordered_for_active_tenant_resolution(self) -> "TenantMembershipModelQuerySet":
        """ Order memberships for deterministic active-tenant resolution.

        Returns:
            TenantMembershipModelQuerySet: Memberships ordered by primary first, then tenant label.
        """
        return self.order_by("-is_primary", "tenant__name", "tenant__slug")

    def primary(self) -> "TenantMembershipModelQuerySet":
        """ Filter memberships marked as primary for their user.

        Returns:
            TenantMembershipModelQuerySet: Primary memberships only.
        """
        return self.filter(is_primary=True)

    def owners(self) -> "TenantMembershipModelQuerySet":
        """ Filter memberships with the owner role.

        Returns:
            TenantMembershipModelQuerySet: Owner memberships only.
        """
        return self.filter(role=TenantRole.OWNER)
