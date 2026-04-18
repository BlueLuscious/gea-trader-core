""" Cart-item persistence model for concrete catalog selections in runtime baskets. """

from typing import TYPE_CHECKING
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from cart.models.managers.cart_item_model_manager import CartItemModelManager

if TYPE_CHECKING:
    from cart.models import CartModel
    from catalog.models import ProductModel, ProductVariantModel


class CartItemModel(models.Model):
    """ Concrete item stored inside a cart. """

    cart: "CartModel" = models.ForeignKey(
        "cart.CartModel",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Cart"),
        help_text=_("Cart this line belongs to."),
    )
    product: "ProductModel" = models.ForeignKey(
        "catalog.ProductModel",
        on_delete=models.PROTECT,
        related_name="cart_items",
        verbose_name=_("Product"),
        help_text=_("Product currently selected in this cart line."),
    )
    variant: "ProductVariantModel | None" = models.ForeignKey(
        "catalog.ProductVariantModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_items",
        verbose_name=_("Variant"),
        help_text=_("Optional variant currently selected for this cart line."),
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Quantity"),
        help_text=_("How many units of the selected product the cart currently holds."),
    )
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Notes"),
        help_text=_("Optional runtime notes captured for this cart line."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("When this cart item was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
        help_text=_("When this cart item was last updated."),
    )

    objects: CartItemModelManager = CartItemModelManager()

    id: int
    cart_id: int
    product_id: int
    variant_id: int | None

    class Meta:
        """ Declarative admin-facing metadata for cart-item persistence. """

        ordering = ("created_at", "id")
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product", "variant"],
                name="cart_item_unique_cart_product_variant",
            ),
            models.UniqueConstraint(
                fields=["cart", "product"],
                condition=Q(variant__isnull=True),
                name="cart_item_unique_cart_product_without_variant",
            ),
        ]
        verbose_name = _("Cart item")
        verbose_name_plural = _("Cart items")

    def __str__(self) -> str:
        """ Return the admin-friendly label for the cart item.

        Returns:
            str: Cart item label.
        """
        return f"Cart item {self.pk}"

    def clean(self) -> None:
        """ Validate catalog relations against the tenant-owned cart boundary.

        Raises:
            ValidationError: When the selected product belongs to another tenant or
            when the selected variant does not belong to the selected product.
        """
        super().clean()
        self._validate_runtime_catalog_scope()

    def save(self, *args: object, **kwargs: object) -> None:
        """ Persist the cart item after validating runtime catalog consistency.

        Args:
            *args: Positional save arguments.
            **kwargs: Keyword save arguments.

        Raises:
            ValidationError: When the selected product belongs to another tenant or
            when the selected variant does not belong to the selected product.
        """
        self._validate_runtime_catalog_scope()
        super().save(*args, **kwargs)

    def _validate_runtime_catalog_scope(self) -> None:
        """ Keep cart items aligned with the tenant-owned cart boundary.

        Raises:
            ValidationError: When a product belongs to another tenant or a variant
            does not belong to the selected product.
        """
        if self.cart_id is None or self.product_id is None:
            return

        if self.cart.tenant_id != self.product.tenant_id:
            raise ValidationError({"product": _("Product must belong to the same business as the cart.")})

        if self.variant_id is not None and self.variant.product_id != self.product_id:
            raise ValidationError({"variant": _("Variant must belong to the selected product.")})
