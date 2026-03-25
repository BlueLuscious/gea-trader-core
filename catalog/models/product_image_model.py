from typing import TYPE_CHECKING
from django.db import models
from catalog.models.managers.product_image_model_manager import ProductImageModelManager

if TYPE_CHECKING:
    from catalog.models import ProductModel, ProductVariantModel


class ProductImageModel(models.Model):
    """ Image resource attached to a product or one of its variants. """

    product: "ProductModel" = models.ForeignKey(
        "catalog.ProductModel",
        on_delete=models.CASCADE,
        related_name="images",
    )
    variant: "ProductVariantModel | None" = models.ForeignKey(
        "catalog.ProductVariantModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="images",
    )
    image = models.ImageField(upload_to="catalog/products/images/")
    alt_text = models.CharField(max_length=255, blank=True, default="")
    sort_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects: ProductImageModelManager = ProductImageModelManager()

    id: int
    product_id: int
    variant_id: int | None

    class Meta:
        ordering = ("product_id", "sort_order", "id")
        verbose_name = "Product image"
        verbose_name_plural = "Product images"

    def __str__(self) -> str:
        """ Return the image label.

        Returns:
            str: Alt text, filename or fallback id.
        """
        return self.alt_text or self.image.name or f"Image {self.pk}"
