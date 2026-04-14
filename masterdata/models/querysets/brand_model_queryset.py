from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from masterdata.models.brand_model import BrandModel


class BrandModelQuerySet(models.QuerySet["BrandModel"]):
    """ QuerySet for reusable brand filters.

    Example:
        BrandModel.objects.active()
    """

    def active(self) -> "BrandModelQuerySet":
        """ Return only active brands.

        Returns:
            BrandModelQuerySet: Filtered queryset with active brands.
        """
        return self.filter(is_active=True)
