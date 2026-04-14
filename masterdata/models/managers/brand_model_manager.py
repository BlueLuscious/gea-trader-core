from typing import TYPE_CHECKING
from django.db import models
from masterdata.models.querysets.brand_model_queryset import BrandModelQuerySet

if TYPE_CHECKING:
    from masterdata.models.brand_model import BrandModel


class BrandModelManager(models.Manager["BrandModel"]):
    """ Manager exposing typed brand queryset helpers. """

    def get_queryset(self) -> "BrandModelQuerySet":
        """ Return the base queryset for brand queries.

        Returns:
            BrandModelQuerySet: Specialized queryset for brands.
        """
        return BrandModelQuerySet(self.model, using=self._db)

    def active(self) -> "BrandModelQuerySet":
        """ Return active brands.

        Returns:
            BrandModelQuerySet: Active brands queryset.
        """
        return self.get_queryset().active()
