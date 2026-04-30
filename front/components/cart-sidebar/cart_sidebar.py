""" Cart sidebar component for the public storefront runtime. """

from typing import NamedTuple
from uuid import uuid4
from django_components import Component, register
from front.components.props import PanelWidth, normalize_bool, normalize_enum


@register("cart_sidebar")
class CartSidebarController(Component):
    """ Render the reusable storefront cart sidebar shell. """

    template_file = "cart-sidebar.html"
    css_file = "cart-sidebar.css"
    js_file = "cart-sidebar.js"

    class Kwargs(NamedTuple):
        """ Typed kwargs accepted by the cart sidebar component. """

        id: str = ""
        class_name: str = ""
        title: str = "Carrito de cotización"
        aria_label: str = "Carrito"
        width: str = PanelWidth.LG.value
        side: str = "right"
        open: bool = False
        empty_title: str = "Tu carrito está vacío"
        empty_copy: str = "Agregá productos para preparar una cotización rápida."
        clear_label: str = "Vaciar"
        quote_label: str = "Solicitar cotización"
        quote_modal_id: str = ""

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict[str, object]:
        """ Build normalized template data for the cart sidebar component.

        Args:
            args: Positional component args.
            kwargs: Typed keyword arguments.
            slots: Available template slots.
            context: Outer rendering context.

        Returns:
            dict[str, object]: Normalized cart sidebar template context.
        """
        component_id = kwargs.id or f"gc-cart-sidebar-{uuid4().hex[:8]}"

        return {
            "id": component_id,
            "sidebar_id": f"{component_id}__sidebar",
            "class_name": kwargs.class_name,
            "title": kwargs.title,
            "aria_label": kwargs.aria_label,
            "width": normalize_enum(kwargs.width, PanelWidth, PanelWidth.LG).value,
            "side": kwargs.side if kwargs.side in {"left", "right"} else "right",
            "open": normalize_bool(kwargs.open),
            "empty_title": kwargs.empty_title,
            "empty_copy": kwargs.empty_copy,
            "clear_label": kwargs.clear_label,
            "quote_label": kwargs.quote_label,
            "clear_button_attrs": {"cart-clear": "true"},
            "quote_modal_id": kwargs.quote_modal_id,
            "quote_button_attrs": {"cart-quote": "true"},
        }
