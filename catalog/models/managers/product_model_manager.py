from typing import TYPE_CHECKING
from django.db import models
from catalog.models.querysets.product_model_queryset import ProductModelQuerySet

if TYPE_CHECKING:
    from catalog.models.product_model import ProductModel


class ProductModelManager(models.Manager["ProductModel"]):
    """ Manager exposing typed product queryset helpers. """

    def get_queryset(self) -> "ProductModelQuerySet":
        """ Return the base queryset for product queries.

        Returns:
            ProductModelQuerySet: A specialized queryset for ProductModel.
        """
        return ProductModelQuerySet(self.model, using=self._db)

    def active(self) -> "ProductModelQuerySet":
        """ Return active products.

        Returns:
            ProductModelQuerySet: Active products queryset.
        """
        return self.get_queryset().active()

    def featured(self) -> "ProductModelQuerySet":
        """ Return featured products.

        Returns:
            ProductModelQuerySet: Featured products queryset.
        """
        return self.get_queryset().featured()

    def requiring_quote(self) -> "ProductModelQuerySet":
        """ Return products in quotation mode.

        Returns:
            ProductModelQuerySet: Quote-enabled products queryset.
        """
        return self.get_queryset().requiring_quote()

    def with_related(self) -> "ProductModelQuerySet":
        """ Return products with brand and category eager loaded.

        Returns:
            ProductModelQuerySet: Queryset with select_related applied.
        """
        return self.get_queryset().with_related()
