from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from masterdata.models.category_model import CategoryModel


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
