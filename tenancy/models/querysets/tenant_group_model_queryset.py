"""Reusable queryset helpers for the tenant-group model."""

from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from django.contrib.auth.models import Group
    from tenancy.models import TenantGroupModel, TenantModel


class TenantGroupModelQuerySet(models.QuerySet["TenantGroupModel"]):
    """QuerySet for reusable tenant-group filters."""

    def for_tenant(self, tenant: "TenantModel") -> "TenantGroupModelQuerySet":
        """Filter tenant-group bindings belonging to one tenant.

        Args:
            tenant: Tenant whose groups should be returned.

        Returns:
            TenantGroupModelQuerySet: Tenant-group bindings linked to the provided tenant.
        """
        return self.filter(tenant=tenant)

    def for_group(self, group: "Group") -> "TenantGroupModelQuerySet":
        """Filter tenant-group bindings for one Django auth group.

        Args:
            group: Django group whose tenant binding should be returned.

        Returns:
            TenantGroupModelQuerySet: Tenant-group bindings linked to the provided group.
        """
        return self.filter(group=group)

    def with_group(self) -> "TenantGroupModelQuerySet":
        """Eager-load the related Django auth group.

        Returns:
            TenantGroupModelQuerySet: Bindings with ``group`` selected.
        """
        return self.select_related("group")

    def with_tenant(self) -> "TenantGroupModelQuerySet":
        """Eager-load the related tenant.

        Returns:
            TenantGroupModelQuerySet: Bindings with ``tenant`` selected.
        """
        return self.select_related("tenant")

    def for_active_tenant(self) -> "TenantGroupModelQuerySet":
        """Filter bindings whose tenant remains active.

        Returns:
            TenantGroupModelQuerySet: Bindings linked to active tenants only.
        """
        return self.filter(tenant__is_active=True)
