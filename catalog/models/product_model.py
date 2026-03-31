from typing import TYPE_CHECKING
from django.db import models
from catalog.models.managers.product_model_manager import ProductModelManager

if TYPE_CHECKING:
    from masterdata.models import BrandModel, CategoryModel


class ProductModel(models.Model):
    """ Catalog product entity used across public site and quotation flow.

    Example:
        ProductModel.objects.with_related().active()
    """

    brand: "BrandModel | None" = models.ForeignKey(
        "masterdata.BrandModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    category: "CategoryModel | None" = models.ForeignKey(
        "masterdata.CategoryModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    short_description = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    sku_base = models.CharField(max_length=64, blank=True, default="")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    requires_quote = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: ProductModelManager = ProductModelManager()

    id: int
    brand_id: int | None
    category_id: int | None

    class Meta:
        ordering = ("name",)
        indexes = [models.Index(fields=["is_active", "is_featured"])]
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self) -> str:
        """ Return the product label.

        Returns:
            str: Product name.
        """
        return self.name
