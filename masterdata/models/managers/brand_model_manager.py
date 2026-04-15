from typing import TYPE_CHECKING
from django.db import models
from masterdata.models.querysets.brand_model_queryset import BrandModelQuerySet

if TYPE_CHECKING:
    from masterdata.models.brand_model import BrandModel
    from tenancy.models import TenantModel


class BrandModelManager(models.Manager["BrandModel"]):
    """ Manager exposing typed brand queryset helpers. """

    def get_queryset(self) -> "BrandModelQuerySet":
        """ Return the base queryset for brand queries.

        Returns:
            BrandModelQuerySet: Specialized queryset for brands.
        """
        return BrandModelQuerySet(self.model, using=self._db)

    def active(self) -> "BrandModelQuerySet":
        """ Return active brands.

        Returns:
            BrandModelQuerySet: Active brands queryset.
        """
        return self.get_queryset().active()

    def for_tenant(self, tenant: "TenantModel") -> "BrandModelQuerySet":
        """ Return brands that belong to one tenant.

        Args:
            tenant: Tenant that owns the brands.

        Returns:
            BrandModelQuerySet: Tenant-scoped brand queryset.
        """
        return self.get_queryset().for_tenant(tenant)
