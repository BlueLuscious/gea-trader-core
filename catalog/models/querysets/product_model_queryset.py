from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from catalog.models.product_model import ProductModel
    from tenancy.models import TenantModel


class ProductModelQuerySet(models.QuerySet["ProductModel"]):
    """ QuerySet for reusable product filters and eager loading. """

    def for_tenant(self, tenant: "TenantModel") -> "ProductModelQuerySet":
        """ Return products scoped to one tenant.

        Args:
            tenant: Tenant that owns the products.

        Returns:
            ProductModelQuerySet: Tenant-scoped products queryset.
        """
        return self.filter(tenant=tenant)

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
