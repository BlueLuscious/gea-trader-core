from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from catalog.models import ProductModel, ProductVariantModel
    from tenancy.models import TenantModel


class ProductVariantModelQuerySet(models.QuerySet["ProductVariantModel"]):
    """ QuerySet for reusable product variant filters. """

    def for_tenant(self, tenant: "TenantModel") -> "ProductVariantModelQuerySet":
        """ Return variants scoped through their product tenant.

        Args:
            tenant: Tenant that owns the parent products.

        Returns:
            ProductVariantModelQuerySet: Tenant-scoped variants queryset.
        """
        return self.filter(product__tenant=tenant)

    def active(self) -> "ProductVariantModelQuerySet":
        """ Return only active variants.

        Returns:
            ProductVariantModelQuerySet: Active variants queryset.
        """
        return self.filter(is_active=True)

    def defaults(self) -> "ProductVariantModelQuerySet":
        """ Return default variants.

        Returns:
            ProductVariantModelQuerySet: Default variants queryset.
        """
        return self.filter(is_default=True)

    def for_product(self, product: "ProductModel") -> "ProductVariantModelQuerySet":
        """ Return variants for a given product.

        Args:
            product: Product instance or compatible lookup value.

        Returns:
            ProductVariantModelQuerySet: Filtered variants queryset.
        """
        return self.filter(product=product)
