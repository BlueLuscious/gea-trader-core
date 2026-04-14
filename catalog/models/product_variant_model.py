from typing import TYPE_CHECKING
from django.db import models
from django.db.models import Q
from catalog.models.managers.product_variant_model_manager import ProductVariantModelManager

if TYPE_CHECKING:
    from catalog.models import ProductModel


class ProductVariantModel(models.Model):
    """ Concrete sellable or quotable variation of a product. """

    product: "ProductModel" = models.ForeignKey(
        "catalog.ProductModel",
        on_delete=models.CASCADE,
        related_name="variants",
    )
    name = models.CharField(max_length=255, blank=True, default="")
    sku = models.CharField(max_length=64, unique=True)
    attributes_json = models.JSONField(blank=True, default=dict)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: ProductVariantModelManager = ProductVariantModelManager()

    id: int
    product_id: int

    class Meta:
        ordering = ("product_id", "sort_order", "name", "id")
        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(is_default=True),
                name="catalog_variant_one_default_per_product",
            ),
        ]
        verbose_name = "Product variant"
        verbose_name_plural = "Product variants"

    def __str__(self) -> str:
        """ Return the variant label.

        Returns:
            str: Variant name or sku.
        """
        return self.name or self.sku
