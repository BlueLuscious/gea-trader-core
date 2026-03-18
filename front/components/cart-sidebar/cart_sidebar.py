from typing import NamedTuple
from uuid import uuid4
from django_components import Component, register
from front.components.props import PanelWidth, normalize_bool, normalize_enum


@register("cart_sidebar")
class CartSidebarController(Component):
    template_file = "cart-sidebar.html"
    css_file = "cart-sidebar.css"
    js_file = "cart-sidebar.js"

    class Kwargs(NamedTuple):
        id: str = ""
        class_name: str = ""
        title: str = "Carrito de cotizacion"
        aria_label: str = "Carrito"
        width: str = PanelWidth.LG.value
        side: str = "right"
        open: bool = False
        empty_title: str = "Tu carrito esta vacio"
        empty_copy: str = "Agrega productos para preparar una cotizacion rapida."
        clear_label: str = "Vaciar"
        quote_label: str = "Solicitar cotizacion"

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict:
        component_id = kwargs.id or f"gc-cart-sidebar-{uuid4().hex[:8]}"

        return dict(
            id=component_id,
            sidebar_id=f"{component_id}__sidebar",
            class_name=kwargs.class_name,
            title=kwargs.title,
            aria_label=kwargs.aria_label,
            width=normalize_enum(kwargs.width, PanelWidth, PanelWidth.LG).value,
            side=kwargs.side if kwargs.side in {"left", "right"} else "right",
            open=normalize_bool(kwargs.open),
            empty_title=kwargs.empty_title,
            empty_copy=kwargs.empty_copy,
            clear_label=kwargs.clear_label,
            quote_label=kwargs.quote_label,
            clear_button_attrs={"cart-clear": "true"},
            quote_button_attrs={"cart-quote": "true"},
        )
