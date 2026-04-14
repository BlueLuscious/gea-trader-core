from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from catalog.models.product_image_model import ProductImageModel
    from tenancy.models import TenantModel


class ProductImageModelQuerySet(models.QuerySet["ProductImageModel"]):
    """ QuerySet for reusable product image filters. """

    def for_tenant(self, tenant: "TenantModel") -> "ProductImageModelQuerySet":
        """ Return images scoped through their product tenant.

        Args:
            tenant: Tenant that owns the parent products.

        Returns:
            ProductImageModelQuerySet: Tenant-scoped images queryset.
        """
        return self.filter(product__tenant=tenant)

    def primary(self) -> "ProductImageModelQuerySet":
        """ Return images marked as primary.

        Returns:
            ProductImageModelQuerySet: Primary images queryset.
        """
        return self.filter(is_primary=True)

    def ordered(self) -> "ProductImageModelQuerySet":
        """ Return images in presentation order.

        Returns:
            ProductImageModelQuerySet: Ordered images queryset.
        """
        return self.order_by("sort_order", "id")
