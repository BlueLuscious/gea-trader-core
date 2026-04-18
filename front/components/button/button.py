from typing import NamedTuple
from uuid import uuid4
from django_components import Component, register
from front.components.props import (
    ButtonRadius,
    ButtonSize,
    ButtonVariant,
    FontSize,
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
        font_size: str = ""
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
        component_id = kwargs.id or f"gc-button-{uuid4().hex[:8]}"
        size = normalize_enum(kwargs.size, ButtonSize, ButtonSize.MD).value
        derived_font_size = kwargs.font_size or {
            ButtonSize.SM.value: FontSize.SM.value,
            ButtonSize.MD.value: FontSize.MD.value,
            ButtonSize.LG.value: FontSize.LG.value,
            ButtonSize.FULL.value: FontSize.MD.value,
        }.get(size, FontSize.MD.value)

        return dict(
            id=component_id,
            type=kwargs.type if kwargs.type in {"button", "submit", "reset"} else "button",
            href=kwargs.href,
            variant=normalize_enum(kwargs.variant, ButtonVariant, ButtonVariant.SOLID).value,
            size=size,
            font_size=normalize_enum(derived_font_size, FontSize, FontSize.MD).value,
            radius=normalize_enum(kwargs.radius, ButtonRadius, ButtonRadius.FULL).value,
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
