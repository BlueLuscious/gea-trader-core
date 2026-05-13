""" HTML fragment renderer for public cart runtime responses. """

from django.template.loader import render_to_string


class CartFragmentRenderer:
    """ Render server-owned cart fragments consumed by the sidebar runtime. """

    def build_cart_items_html(self, items: list[dict[str, object]]) -> str:
        """ Render cart-item HTML for the sidebar body.

        Args:
            items: Serialized cart-item payloads.

        Returns:
            str: Rendered cart items HTML.
        """
        return "".join(
            render_to_string("cart/runtime/cart_item.html", {"item": item})
            for item in items
        )

    def build_cart_summary_html(self, *, count: int) -> str:
        """ Render the cart summary block for the sidebar body.

        Args:
            count: Total cart line count.

        Returns:
            str: Rendered summary HTML.
        """
        return render_to_string(
            "cart/runtime/cart_summary.html",
            {
                "count": count,
            },
        )
