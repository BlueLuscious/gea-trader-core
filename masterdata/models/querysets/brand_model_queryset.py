from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from masterdata.models.brand_model import BrandModel
    from tenancy.models import TenantModel


class BrandModelQuerySet(models.QuerySet["BrandModel"]):
    """ QuerySet for reusable brand filters.

    Example:
        BrandModel.objects.active()
    """

    def active(self) -> "BrandModelQuerySet":
        """ Return only active brands.

        Returns:
            BrandModelQuerySet: Filtered queryset with active brands.
        """
        return self.filter(is_active=True)

    def for_tenant(self, tenant: "TenantModel") -> "BrandModelQuerySet":
        """ Return brands that belong to one tenant.

        Args:
            tenant: Tenant that owns the brands.

        Returns:
            BrandModelQuerySet: Tenant-scoped brand queryset.
        """
        return self.filter(tenant=tenant)
