from typing import NamedTuple
from uuid import uuid4
from django_components import Component, register
from front.components.props import FontSize, SwitchSize, normalize_bool, normalize_enum


@register("switch")
class SwitchController(Component):
    template_file = "switch.html"
    css_file = "switch.css"
    js_file = "switch.js"

    class Kwargs(NamedTuple):
        id: str = ""
        name: str = ""
        class_name: str = ""
        size: str = SwitchSize.MD.value
        font_size: str = ""
        checked: bool = False
        disabled: bool = False
        icon_only: bool = False
        aria_label: str = ""
        label_left: str = ""
        label_right: str = ""
        icon_left: str = ""
        icon_right: str = ""
        peer_label: str = ""

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict:
        component_id = kwargs.id or f"gc-switch-{uuid4().hex[:8]}"
        size = normalize_enum(kwargs.size, SwitchSize, SwitchSize.MD).value
        derived_font_size = kwargs.font_size or {
            SwitchSize.SM.value: FontSize.SM.value,
            SwitchSize.MD.value: FontSize.MD.value,
            SwitchSize.LG.value: FontSize.LG.value,
            SwitchSize.FULL.value: FontSize.MD.value,
        }.get(size, FontSize.MD.value)

        return dict(
            id=component_id,
            name=kwargs.name,
            class_name=kwargs.class_name,
            size=size,
            font_size=normalize_enum(derived_font_size, FontSize, FontSize.MD).value,
            checked=normalize_bool(kwargs.checked),
            disabled=normalize_bool(kwargs.disabled),
            icon_only=normalize_bool(kwargs.icon_only),
            aria_label=kwargs.aria_label,
            label_left=kwargs.label_left,
            label_right=kwargs.label_right,
            icon_left=kwargs.icon_left.removeprefix("fa-").strip().lower(),
            icon_right=kwargs.icon_right.removeprefix("fa-").strip().lower(),
            peer_label=kwargs.peer_label,
        )
