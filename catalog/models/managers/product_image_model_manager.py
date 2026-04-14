from typing import TYPE_CHECKING
from django.db import models
from catalog.models.querysets.product_image_model_queryset import ProductImageModelQuerySet

if TYPE_CHECKING:
    from catalog.models.product_image_model import ProductImageModel
    from tenancy.models import TenantModel


class ProductImageModelManager(models.Manager["ProductImageModel"]):
    """ Manager exposing typed product image queryset helpers. """

    def get_queryset(self) -> "ProductImageModelQuerySet":
        """ Return the base queryset for product image queries.

        Returns:
            ProductImageModelQuerySet: Specialized queryset for images.
        """
        return ProductImageModelQuerySet(self.model, using=self._db)

    def primary(self) -> "ProductImageModelQuerySet":
        """ Return primary images.

        Returns:
            ProductImageModelQuerySet: Primary images queryset.
        """
        return self.get_queryset().primary()

    def for_tenant(self, tenant: "TenantModel") -> "ProductImageModelQuerySet":
        """ Return images scoped through their product tenant.

        Args:
            tenant: Tenant that owns the parent products.

        Returns:
            ProductImageModelQuerySet: Tenant-scoped images queryset.
        """
        return self.get_queryset().for_tenant(tenant)

    def ordered(self) -> "ProductImageModelQuerySet":
        """ Return ordered images.

        Returns:
            ProductImageModelQuerySet: Ordered images queryset.
        """
        return self.get_queryset().ordered()
