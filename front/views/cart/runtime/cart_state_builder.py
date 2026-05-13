""" Cart-state builder for public cart runtime responses. """

from decimal import Decimal
from django.urls import reverse
from cart.models import CartItemModel, CartModel
from .cart_fragment_renderer import CartFragmentRenderer


class CartStateBuilder:
    """ Build the public cart runtime JSON contract and related fragments. """

    def __init__(self, *, fragment_renderer: CartFragmentRenderer | None = None) -> None:
        """ Initialize the builder with its HTML fragment renderer.

        Args:
            fragment_renderer: Optional renderer used for server-owned fragments.
        """
        self.fragment_renderer = fragment_renderer or CartFragmentRenderer()

    def build_cart_item_payload(self, item: CartItemModel) -> dict[str, object]:
        """ Build one serialized cart-item payload for the public sidebar.

        Args:
            item: Persisted cart item.

        Returns:
            dict[str, object]: Serialized item ready for runtime rendering.
        """
        product = item.product
        variant = item.variant
        resolved_price = variant.price if variant is not None else product.get_public_price()
        image_url = (
            product.get_variant_image_url(variant)
            if variant is not None
            else product.get_preferred_image_url()
        )
        title = product.name
        subtitle = variant.name if variant is not None and variant.name else ""
        return {
            "id": item.id,
            "product_id": product.id,
            "variant_id": variant.id if variant is not None else None,
            "title": title,
            "subtitle": subtitle,
            "sku": variant.sku if variant is not None else product.sku_base,
            "image_url": image_url,
            "href": reverse("product_detail", kwargs={"slug": product.slug}),
            "quantity": item.quantity,
            "price": str(resolved_price) if resolved_price is not None else "",
            "price_text": (
                f"ARS {resolved_price:.2f}"
                if isinstance(resolved_price, Decimal)
                else ""
            ),
            "notes": item.notes,
        }

    def build_cart_state(self, cart: CartModel | None) -> dict[str, object]:
        """ Build one serialized cart state for the current request.

        Args:
            cart: Persisted active cart when one exists.

        Returns:
            dict[str, object]: Serialized cart state.
        """
        if cart is None:
            return {
                "cart_id": None,
                "status": "",
                "items": [],
                "count": 0,
                "items_html": "",
                "summary_html": "",
            }

        items = [
            self.build_cart_item_payload(item)
            for item in CartItemModel.objects.for_cart(cart).with_catalog().order_by("created_at", "id")
        ]
        line_count = len(items)
        return {
            "cart_id": cart.id,
            "status": cart.status,
            "items": items,
            "count": line_count,
            "items_html": self.fragment_renderer.build_cart_items_html(items),
            "summary_html": self.fragment_renderer.build_cart_summary_html(count=line_count),
        }
