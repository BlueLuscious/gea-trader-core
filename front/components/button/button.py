from typing import NamedTuple
from uuid import uuid4
from django_components import Component, register
from front.components.props import (
    ButtonRadius,
    ButtonSize,
    ButtonVariant,
    IconStyle,
    normalize_bool,
    normalize_data_attributes,
    normalize_enum,
)


@register("button")
class ButtonController(Component):
    template_file = "button.html"
    css_file = "button.css"
    js_file = "button.js"

    class Kwargs(NamedTuple):
        id: str = ""
        type: str = "button"
        href: str = ""
        variant: str = ButtonVariant.SOLID.value
        size: str = ButtonSize.MD.value
        radius: str = ButtonRadius.FULL.value
        class_name: str = ""
        disabled: bool = False
        aria_label: str = ""
        icon_left_name: str = ""
        icon_left_style: str = IconStyle.SOLID.value
        icon_left_size: str = ""
        icon_right_name: str = ""
        icon_right_style: str = IconStyle.SOLID.value
        icon_right_size: str = ""
        icon_only: bool = False
        toggle: bool = False
        pressed: bool = False
        data_attrs: dict | None = None

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict:
        variant = normalize_enum(kwargs.variant, ButtonVariant, ButtonVariant.SOLID).value
        size = normalize_enum(kwargs.size, ButtonSize, ButtonSize.MD).value
        radius = normalize_enum(kwargs.radius, ButtonRadius, ButtonRadius.FULL).value
        component_id = kwargs.id or f"gc-button-{uuid4().hex[:8]}"

        return dict(
            id=component_id,
            type=kwargs.type if kwargs.type in {"button", "submit", "reset"} else "button",
            href=kwargs.href,
            variant=variant,
            size=size,
            radius=radius,
            class_name=kwargs.class_name,
            disabled=normalize_bool(kwargs.disabled),
            aria_label=kwargs.aria_label,
            icon_left_name=kwargs.icon_left_name.removeprefix("fa-").strip(),
            icon_left_style=normalize_enum(kwargs.icon_left_style, IconStyle, IconStyle.SOLID).value,
            icon_left_size=kwargs.icon_left_size.removeprefix("fa-").strip(),
            icon_right_name=kwargs.icon_right_name.removeprefix("fa-").strip(),
            icon_right_style=normalize_enum(kwargs.icon_right_style, IconStyle, IconStyle.SOLID).value,
            icon_right_size=kwargs.icon_right_size.removeprefix("fa-").strip(),
            icon_only=normalize_bool(kwargs.icon_only),
            toggle=normalize_bool(kwargs.toggle),
            pressed=normalize_bool(kwargs.pressed),
            data_attrs=normalize_data_attributes(kwargs.data_attrs),
        )
