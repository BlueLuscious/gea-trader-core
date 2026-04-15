from typing import TYPE_CHECKING
from django.db import models
from masterdata.models.querysets.category_model_queryset import CategoryModelQuerySet

if TYPE_CHECKING:
    from masterdata.models.category_model import CategoryModel
    from tenancy.models import TenantModel


class CategoryModelManager(models.Manager["CategoryModel"]):
    """ Manager exposing typed category queryset helpers. """

    def get_queryset(self) -> "CategoryModelQuerySet":
        """ Return the base queryset for category queries.

        Returns:
            CategoryModelQuerySet: Specialized queryset for categories.
        """
        return CategoryModelQuerySet(self.model, using=self._db)

    def active(self) -> "CategoryModelQuerySet":
        """ Return active categories.

        Returns:
            CategoryModelQuerySet: Active categories queryset.
        """
        return self.get_queryset().active()

    def roots(self) -> "CategoryModelQuerySet":
        """ Return root categories.

        Returns:
            CategoryModelQuerySet: Root categories queryset.
        """
        return self.get_queryset().roots()

    def for_tenant(self, tenant: "TenantModel") -> "CategoryModelQuerySet":
        """ Return categories that belong to one tenant.

        Args:
            tenant: Tenant that owns the categories.

        Returns:
            CategoryModelQuerySet: Tenant-scoped category queryset.
        """
        return self.get_queryset().for_tenant(tenant)
