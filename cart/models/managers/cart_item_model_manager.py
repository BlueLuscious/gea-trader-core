from typing import TYPE_CHECKING
from django.db import models
from cart.models.querysets.cart_item_model_queryset import CartItemModelQuerySet

if TYPE_CHECKING:
    from cart.models import CartItemModel, CartModel


class CartItemModelManager(models.Manager["CartItemModel"]):
    """ Manager exposing typed cart item queryset helpers. """

    def get_queryset(self) -> "CartItemModelQuerySet":
        """ Return the base queryset for cart item queries.

        Returns:
            CartItemModelQuerySet: Specialized queryset for cart items.
        """
        return CartItemModelQuerySet(self.model, using=self._db)

    def with_catalog(self) -> "CartItemModelQuerySet":
        """ Return cart items with catalog relations eager loaded.

        Returns:
            CartItemModelQuerySet: Queryset with product and variant loaded.
        """
        return self.get_queryset().with_catalog()

    def for_cart(self, cart: "CartModel") -> "CartItemModelQuerySet":
        """ Return items for a cart.

        Args:
            cart: Cart instance or compatible lookup value.

        Returns:
            CartItemModelQuerySet: Cart items queryset.
        """
        return self.get_queryset().for_cart(cart)
