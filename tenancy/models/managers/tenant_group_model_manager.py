"""Custom manager for the tenant-group model."""

from typing import TYPE_CHECKING
from django.db import models
from tenancy.models.querysets.tenant_group_model_queryset import TenantGroupModelQuerySet

if TYPE_CHECKING:
    from django.contrib.auth.models import Group
    from tenancy.models import TenantGroupModel, TenantModel


class TenantGroupModelManager(models.Manager["TenantGroupModel"]):
    """Manager exposing typed tenant-group queryset helpers."""

    def get_queryset(self) -> TenantGroupModelQuerySet:
        """Return the base queryset for tenant-group queries.

        Returns:
            TenantGroupModelQuerySet: Specialized queryset for TenantGroupModel.
        """
        return TenantGroupModelQuerySet(self.model, using=self._db)

    def for_tenant(self, tenant: "TenantModel") -> TenantGroupModelQuerySet:
        """Return tenant-group bindings related to one tenant.

        Args:
            tenant: Tenant whose group bindings should be returned.

        Returns:
            TenantGroupModelQuerySet: Bindings linked to the provided tenant.
        """
        return self.get_queryset().for_tenant(tenant)

    def for_group(self, group: "Group") -> TenantGroupModelQuerySet:
        """Return tenant-group bindings for one Django auth group.

        Args:
            group: Django group whose tenant binding should be returned.

        Returns:
            TenantGroupModelQuerySet: Bindings linked to the provided group.
        """
        return self.get_queryset().for_group(group)

    def with_group(self) -> TenantGroupModelQuerySet:
        """Return bindings with the related group eager-loaded.

        Returns:
            TenantGroupModelQuerySet: Bindings with ``group`` selected.
        """
        return self.get_queryset().with_group()

    def with_tenant(self) -> TenantGroupModelQuerySet:
        """Return bindings with the related tenant eager-loaded.

        Returns:
            TenantGroupModelQuerySet: Bindings with ``tenant`` selected.
        """
        return self.get_queryset().with_tenant()

    def for_active_tenant(self) -> TenantGroupModelQuerySet:
        """Return bindings whose tenant remains active.

        Returns:
            TenantGroupModelQuerySet: Bindings linked to active tenants only.
        """
        return self.get_queryset().for_active_tenant()
