from typing import TYPE_CHECKING
from django.db import models
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
    )
    product: "ProductModel | None" = models.ForeignKey(
        "catalog.ProductModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quote_items",
    )
    variant: "ProductVariantModel | None" = models.ForeignKey(
        "catalog.ProductVariantModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quote_items",
    )
    product_name_snapshot = models.CharField(max_length=255)
    sku_snapshot = models.CharField(max_length=64, blank=True, default="")
    attributes_snapshot = models.JSONField(blank=True, default=dict)
    unit_price_snapshot = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    id: int
    quote_id: int
    product_id: int | None
    variant_id: int | None

    objects: QuoteItemModelManager = QuoteItemModelManager()

    class Meta:
        ordering = ("created_at", "id")
        verbose_name = "Quote item"
        verbose_name_plural = "Quote items"

    def __str__(self) -> str:
        """ Return the admin-friendly label for the quote item.

        Returns:
            str: Snapshot name.
        """
        return self.product_name_snapshot
