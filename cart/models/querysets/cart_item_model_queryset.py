from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from cart.models import CartItemModel, CartModel


class CartItemModelQuerySet(models.QuerySet["CartItemModel"]):
    """ QuerySet for reusable cart item filters. """

    def with_catalog(self) -> "CartItemModelQuerySet":
        """ Eager load product and variant relations.

        Returns:
            CartItemModelQuerySet: Queryset with catalog relations loaded.
        """
        return self.select_related("product", "variant")

    def for_cart(self, cart: "CartModel") -> "CartItemModelQuerySet":
        """ Return items for a cart.

        Args:
            cart: Cart instance or compatible lookup value.

        Returns:
            CartItemModelQuerySet: Cart items queryset.
        """
        return self.filter(cart=cart)
