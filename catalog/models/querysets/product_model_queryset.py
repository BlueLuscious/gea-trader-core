from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from catalog.models.product_model import ProductModel


class ProductModelQuerySet(models.QuerySet["ProductModel"]):
    """ QuerySet for reusable product filters and eager loading. """

    def active(self) -> "ProductModelQuerySet":
        """ Return only active products.

        Returns:
            ProductModelQuerySet: Active products queryset.
        """
        return self.filter(is_active=True)

    def featured(self) -> "ProductModelQuerySet":
        """ Return only featured products.

        Returns:
            ProductModelQuerySet: Featured products queryset.
        """
        return self.filter(is_featured=True)

    def requiring_quote(self) -> "ProductModelQuerySet":
        """ Return products that require quotation.

        Returns:
            ProductModelQuerySet: Products flagged for quotation flow.
        """
        return self.filter(requires_quote=True)

    def with_related(self) -> "ProductModelQuerySet":
        """ Eager load brand and category relations.

        Returns:
            ProductModelQuerySet: Queryset with select_related applied.
        """
        return self.select_related("brand", "category")
