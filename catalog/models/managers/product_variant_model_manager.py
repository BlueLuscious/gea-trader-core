from typing import TYPE_CHECKING
from django.db import models
from catalog.models.querysets.product_variant_model_queryset import ProductVariantModelQuerySet

if TYPE_CHECKING:
    from catalog.models import ProductModel, ProductVariantModel


class ProductVariantModelManager(models.Manager["ProductVariantModel"]):
    """ Manager exposing typed product variant queryset helpers. """

    def get_queryset(self) -> "ProductVariantModelQuerySet":
        """ Return the base queryset for product variant queries.

        Returns:
            ProductVariantModelQuerySet: Specialized queryset for variants.
        """
        return ProductVariantModelQuerySet(self.model, using=self._db)

    def active(self) -> "ProductVariantModelQuerySet":
        """ Return active variants.

        Returns:
            ProductVariantModelQuerySet: Active variants queryset.
        """
        return self.get_queryset().active()

    def defaults(self) -> "ProductVariantModelQuerySet":
        """ Return default variants.

        Returns:
            ProductVariantModelQuerySet: Default variants queryset.
        """
        return self.get_queryset().defaults()

    def for_product(self, product: "ProductModel") -> "ProductVariantModelQuerySet":
        """ Return variants for a product.

        Args:
            product: Product instance or compatible lookup value.

        Returns:
            ProductVariantModelQuerySet: Product variants queryset.
        """
        return self.get_queryset().for_product(product)
