""" Custom manager for the tenant-branding model. """

from typing import TYPE_CHECKING
from django.db import models
from tenancy.models.querysets.tenant_branding_model_queryset import TenantBrandingModelQuerySet

if TYPE_CHECKING:
    from tenancy.models import TenantBrandingModel, TenantModel


class TenantBrandingModelManager(models.Manager["TenantBrandingModel"]):
    """ Manager exposing typed tenant-branding queryset helpers. """

    def get_queryset(self) -> TenantBrandingModelQuerySet:
        """ Return the base queryset for tenant-branding queries.

        Returns:
            TenantBrandingModelQuerySet: Specialized queryset for TenantBrandingModel.
        """
        return TenantBrandingModelQuerySet(self.model, using=self._db)

    def for_tenant(self, tenant: "TenantModel") -> TenantBrandingModelQuerySet:
        """ Return branding related to one tenant.

        Args:
            tenant: Tenant whose branding should be returned.

        Returns:
            TenantBrandingModelQuerySet: Branding linked to the provided tenant.
        """
        return self.get_queryset().for_tenant(tenant)

    def with_tenant(self) -> TenantBrandingModelQuerySet:
        """ Return branding with the related tenant eager-loaded.

        Returns:
            TenantBrandingModelQuerySet: Branding with ``tenant`` selected.
        """
        return self.get_queryset().with_tenant()

    def configured(self) -> TenantBrandingModelQuerySet:
        """ Return branding rows that already contain visible branding data.

        Returns:
            TenantBrandingModelQuerySet: Branding rows with at least one configured field.
        """
        return self.get_queryset().configured()
