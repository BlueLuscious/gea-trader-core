from django.db import models
from masterdata.models.managers.brand_model_manager import BrandModelManager


class BrandModel(models.Model):
    """ Master brand entity shared across domains.

    Example:
        BrandModel.objects.create(name="GEA", slug="gea")
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: BrandModelManager = BrandModelManager()

    id: int

    class Meta:
        ordering = ("name",)
        verbose_name = "Brand"
        verbose_name_plural = "Brands"

    def __str__(self) -> str:
        """ Return the admin-friendly label for the brand.

        Returns:
            str: Brand name.
        """
        return self.name
