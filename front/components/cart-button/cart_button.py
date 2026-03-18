from typing import NamedTuple
from uuid import uuid4
from django_components import Component, register
from front.components.props import ButtonRadius, ButtonSize, ButtonVariant, normalize_bool, normalize_enum, normalize_int


@register("cart_button")
class CartButtonController(Component):
    template_file = "cart-button.html"
    css_file = "cart-button.css"
    js_file = "cart-button.js"

    class Kwargs(NamedTuple):
        id: str = ""
        class_name: str = ""
        variant: str = ButtonVariant.OUTLINE.value
        size: str = ButtonSize.MD.value
        radius: str = ButtonRadius.FULL.value
        label: str = "Carrito"
        aria_label: str = "Abrir carrito"
        icon_only: bool = False
        initial_count: int = 0

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict:
        component_id = kwargs.id or f"gc-cart-button-{uuid4().hex[:8]}"
        button_id = f"{component_id}__button"
        initial_count = normalize_int(kwargs.initial_count, default=0, minimum=0)

        return dict(
            id=component_id,
            button_id=button_id,
            class_name=kwargs.class_name,
            variant=normalize_enum(kwargs.variant, ButtonVariant, ButtonVariant.OUTLINE).value,
            size=normalize_enum(kwargs.size, ButtonSize, ButtonSize.MD).value,
            radius=normalize_enum(kwargs.radius, ButtonRadius, ButtonRadius.FULL).value,
            label=kwargs.label,
            aria_label=kwargs.aria_label,
            icon_only=normalize_bool(kwargs.icon_only),
            initial_count=initial_count,
            has_items=initial_count > 0,
        )
