""" Quote-item persistence model for catalog snapshots captured inside a quote. """

from typing import TYPE_CHECKING
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from quotation.models.managers.quote_item_model_manager import QuoteItemModelManager

if TYPE_CHECKING:
    from catalog.models import ProductModel, ProductVariantModel
    from quotation.models import QuoteModel


class QuoteItemModel(models.Model):
    """ Snapshot item stored inside a persisted quote. """

    quote: "QuoteModel" = models.ForeignKey(
        "quotation.QuoteModel",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Quote"),
        help_text=_("Quote this line item belongs to."),
    )
    product: "ProductModel | None" = models.ForeignKey(
        "catalog.ProductModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quote_items",
        verbose_name=_("Product"),
        help_text=_("Optional product reference kept while the catalog product still exists."),
    )
    variant: "ProductVariantModel | None" = models.ForeignKey(
        "catalog.ProductVariantModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quote_items",
        verbose_name=_("Variant"),
        help_text=_("Optional variant reference kept while the catalog variant still exists."),
    )
    product_name_snapshot = models.CharField(
        max_length=255,
        verbose_name=_("Product name snapshot"),
        help_text=_("Product name captured when this quote item was created."),
    )
    sku_snapshot = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name=_("SKU snapshot"),
        help_text=_("SKU captured when this quote item was created."),
    )
    attributes_snapshot = models.JSONField(
        blank=True,
        default=dict,
        verbose_name=_("Attribute snapshot"),
        help_text=_("Variant attributes captured when this quote item was created."),
    )
    unit_price_snapshot = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Unit price snapshot"),
        help_text=_("Unit price captured when this quote item was created."),
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_("Quantity"),
        help_text=_("Number of units requested for this quote item."),
    )
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Item notes"),
        help_text=_("Optional internal note for this specific quote item."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("When this quote item was created."),
    )

    id: int
    quote_id: int
    product_id: int | None
    variant_id: int | None

    objects: QuoteItemModelManager = QuoteItemModelManager()

    class Meta:
        """ Declarative admin-facing metadata for quote-item persistence. """

        ordering = ("created_at", "id")
        verbose_name = _("Quote item")
        verbose_name_plural = _("Quote items")

    def __str__(self) -> str:
        """ Return the admin-friendly label for the quote item.

        Returns:
            str: Snapshot name.
        """
        return self.product_name_snapshot
