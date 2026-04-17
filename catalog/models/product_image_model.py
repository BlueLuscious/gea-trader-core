from typing import TYPE_CHECKING
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from catalog.models.managers.product_image_model_manager import ProductImageModelManager

if TYPE_CHECKING:
    from catalog.models import ProductModel, ProductVariantModel


class ProductImageModel(models.Model):
    """ Image resource attached to a product or one of its variants. """

    product: "ProductModel" = models.ForeignKey(
        "catalog.ProductModel",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Product"),
        help_text=_("Product this image belongs to."),
    )
    variant: "ProductVariantModel | None" = models.ForeignKey(
        "catalog.ProductVariantModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="images",
        verbose_name=_("Variant"),
        help_text=_("Optional variant shown by this image when it is not shared across the whole product."),
    )
    image = models.ImageField(
        upload_to="catalog/products/images/",
        verbose_name=_("Image file"),
        help_text=_("Upload the product image shown in the catalog and admin."),
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Alt text"),
        help_text=_("Short accessibility description of what appears in the image."),
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display order"),
        help_text=_("Lower values appear first in product galleries."),
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("Primary image"),
        help_text=_("Use this image as the main visual for the product or variant."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("When this image was created."),
    )

    objects: ProductImageModelManager = ProductImageModelManager()

    id: int
    product_id: int
    variant_id: int | None

    class Meta:
        ordering = ("product_id", "sort_order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(variant__isnull=True, is_primary=True),
                name="catalog_image_one_primary_root_per_product",
            ),
            models.UniqueConstraint(
                fields=["variant"],
                condition=Q(variant__isnull=False, is_primary=True),
                name="catalog_image_one_primary_per_variant",
            ),
        ]
        verbose_name = _("Product image")
        verbose_name_plural = _("Product images")

    def clean(self) -> None:
        """ Validate product-image relationships before persistence.

        Raises:
            ValidationError: When the selected variant belongs to another product.
        """
        super().clean()

        if self.variant_id is None:
            return

        if self.variant is not None and self.variant.product_id != self.product_id:
            raise ValidationError({"variant": _("Choose a variant that belongs to the selected product.")})

    def __str__(self) -> str:
        """ Return the image label.

        Returns:
            str: Alt text, filename or fallback id.
        """
        return self.alt_text or self.image.name or f"Image {self.pk}"
