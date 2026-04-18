from typing import NamedTuple
from uuid import uuid4
from django_components import Component, register
from front.components.props import FontSize, SwitchSize, normalize_bool, normalize_enum


@register("theme_switch")
class ThemeSwitchController(Component):
    template_file = "theme-switch.html"
    css_file = "theme-switch.css"
    js_file = "theme-switch.js"

    class Kwargs(NamedTuple):
        id: str = ""
        class_name: str = ""
        size: str = SwitchSize.MD.value
        font_size: str = ""
        aria_label: str = "Cambiar tema"
        light_icon: str = "sun"
        dark_icon: str = "moon"
        light_label: str = "Claro"
        dark_label: str = "Oscuro"
        peer_label: str = ""
        icon_only: bool = False

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict:
        component_id = kwargs.id or f"gc-theme-switch-{uuid4().hex[:8]}"
        switch_id = f"{component_id}__switch"

        return dict(
            id=component_id,
            switch_id=switch_id,
            class_name=kwargs.class_name,
            size=normalize_enum(kwargs.size, SwitchSize, SwitchSize.MD).value,
            font_size=normalize_enum(kwargs.font_size or kwargs.size or FontSize.MD.value, FontSize, FontSize.MD).value,
            aria_label=kwargs.aria_label,
            light_icon=kwargs.light_icon.removeprefix("fa-").strip().lower(),
            dark_icon=kwargs.dark_icon.removeprefix("fa-").strip().lower(),
            light_label=kwargs.light_label,
            dark_label=kwargs.dark_label,
            peer_label=kwargs.peer_label,
            icon_only=normalize_bool(kwargs.icon_only),
        )
