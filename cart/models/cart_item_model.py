from typing import TYPE_CHECKING
from django.db import models
from django.db.models import Q
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
    )
    product: "ProductModel" = models.ForeignKey(
        "catalog.ProductModel",
        on_delete=models.PROTECT,
        related_name="cart_items",
    )
    variant: "ProductVariantModel | None" = models.ForeignKey(
        "catalog.ProductVariantModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: CartItemModelManager = CartItemModelManager()
    
    id: int
    cart_id: int
    product_id: int
    variant_id: int | None

    class Meta:
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
        verbose_name = "Cart item"
        verbose_name_plural = "Cart items"

    def __str__(self) -> str:
        """ Return the admin-friendly label for the cart item.

        Returns:
            str: Cart item label.
        """
        return f"Cart item {self.pk}"
