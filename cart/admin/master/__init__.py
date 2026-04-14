""" Master admin registrations for the cart app. """

from cart.admin.master.cart_item_model_admin import CartItemModelAdmin
from cart.admin.master.cart_model_admin import CartModelAdmin

__all__: list[str] = ["CartModelAdmin", "CartItemModelAdmin"]
