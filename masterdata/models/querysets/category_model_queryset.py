from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from masterdata.models.category_model import CategoryModel
    from tenancy.models import TenantModel


class CategoryModelQuerySet(models.QuerySet["CategoryModel"]):
    """ QuerySet for reusable category filters.

    Example:
        CategoryModel.objects.active().roots()
    """

    def active(self) -> "CategoryModelQuerySet":
        """ Return only active categories.

        Returns:
            CategoryModelQuerySet: Filtered queryset with active categories.
        """
        return self.filter(is_active=True)

    def roots(self) -> "CategoryModelQuerySet":
        """ Return only root categories.

        Returns:
            CategoryModelQuerySet: Categories without parent.
        """
        return self.filter(parent__isnull=True)

    def featured(self) -> "CategoryModelQuerySet":
        """ Return only categories marked for curated storefront placement.

        Returns:
            CategoryModelQuerySet: Featured categories queryset.
        """
        return self.filter(is_featured=True)

    def for_tenant(self, tenant: "TenantModel") -> "CategoryModelQuerySet":
        """ Return categories that belong to one tenant.

        Args:
            tenant: Tenant that owns the categories.

        Returns:
            CategoryModelQuerySet: Tenant-scoped category queryset.
        """
        return self.filter(tenant=tenant)
