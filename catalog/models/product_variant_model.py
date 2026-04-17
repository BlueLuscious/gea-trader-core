from typing import TYPE_CHECKING
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from catalog.models.managers.product_variant_model_manager import ProductVariantModelManager

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager
    from catalog.models import ProductModel
    from catalog.models.querysets import ProductImageModelQuerySet


class ProductVariantModel(models.Model):
    """ Concrete sellable or quotable variation of a product. """

    product: "ProductModel" = models.ForeignKey(
        "catalog.ProductModel",
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name=_("Product"),
        help_text=_("Product this variant belongs to."),
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Variant name"),
        help_text=_("Optional customer-facing name for this specific variant."),
    )
    sku = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_("Variant SKU"),
        help_text=_("Unique internal reference for this variant."),
    )
    attributes_json = models.JSONField(
        blank=True,
        default=dict,
        verbose_name=_("Variant attributes"),
        help_text=_("Structured attributes such as size, color, or packaging."),
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Price"),
        help_text=_("Optional direct price for this variant when it does not rely only on quotes."),
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Default variant"),
        help_text=_("Use this as the preselected variant for the product."),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Available for selection"),
        help_text=_("Turn this off to keep the variant without offering it."),
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display order"),
        help_text=_("Lower values appear first in admin and customer-facing variant lists."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("When this variant was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
        help_text=_("When this variant was last updated."),
    )

    objects: ProductVariantModelManager = ProductVariantModelManager()

    id: int
    product_id: int
    images: "RelatedManager[ProductImageModelQuerySet]"

    class Meta:
        ordering = ("product_id", "sort_order", "name", "id")
        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(is_default=True),
                name="catalog_variant_one_default_per_product",
            ),
        ]
        verbose_name = _("Product variant")
        verbose_name_plural = _("Product variants")

    def __str__(self) -> str:
        """ Return the variant label.

        Returns:
            str: Variant name or sku.
        """
        return self.name or self.sku
