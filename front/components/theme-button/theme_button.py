from typing import NamedTuple
from uuid import uuid4
from django_components import Component, register
from front.components.props import (
    ButtonRadius,
    ButtonSize,
    ButtonVariant,
    FontSize,
    ThemeIntent,
    normalize_bool,
    normalize_enum
)


@register("theme_button")
class ThemeButtonController(Component):
    template_file = "theme-button.html"
    css_file = "theme-button.css"
    js_file = "theme-button.js"

    class Kwargs(NamedTuple):
        id: str = ""
        class_name: str = ""
        variant: str = ButtonVariant.OUTLINE.value
        size: str = ButtonSize.MD.value
        font_size: str = ""
        radius: str = ButtonRadius.FULL.value
        intent: str = ThemeIntent.TOGGLE.value
        aria_label: str = "Cambiar tema"
        light_icon: str = "sun"
        dark_icon: str = "moon"
        system_icon: str = "desktop"
        light_label: str = "Claro"
        dark_label: str = "Oscuro"
        system_label: str = "Sistema"
        icon_only: bool = False

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict:
        component_id = kwargs.id or f"gc-theme-button-{uuid4().hex[:8]}"
        button_id = f"{component_id}__button"

        return dict(
            id=component_id,
            button_id=button_id,
            class_name=kwargs.class_name,
            variant=normalize_enum(kwargs.variant, ButtonVariant, ButtonVariant.OUTLINE).value,
            size=normalize_enum(kwargs.size, ButtonSize, ButtonSize.MD).value,
            font_size=normalize_enum(kwargs.font_size or kwargs.size or FontSize.MD.value, FontSize, FontSize.MD).value,
            radius=normalize_enum(kwargs.radius, ButtonRadius, ButtonRadius.FULL).value,
            intent=normalize_enum(kwargs.intent, ThemeIntent, ThemeIntent.TOGGLE).value,
            aria_label=kwargs.aria_label,
            light_icon=kwargs.light_icon.removeprefix("fa-").strip().lower(),
            dark_icon=kwargs.dark_icon.removeprefix("fa-").strip().lower(),
            system_icon=kwargs.system_icon.removeprefix("fa-").strip().lower(),
            light_label=kwargs.light_label,
            dark_label=kwargs.dark_label,
            system_label=kwargs.system_label,
            icon_only=normalize_bool(kwargs.icon_only),
        )
