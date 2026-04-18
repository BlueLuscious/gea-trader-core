from typing import NamedTuple
from uuid import uuid4
from django_components import Component, register, Slot
from front.components.props import ShadowSize, normalize_bool, normalize_enum


@register("appbar")
class AppbarController(Component):
    template_file = "appbar.html"
    css_file = "appbar.css"

    class Kwargs(NamedTuple):
        id: str = ""
        class_name: str = ""
        sticky: bool = True
        bordered: bool = True
        shadow: str = ShadowSize.NONE.value
        aria_label: str = "Barra de aplicacion"

    def get_template_data(self, args, kwargs: Kwargs, slots: dict[str, Slot], context) -> dict:
        component_id = kwargs.id or f"gc-appbar-{uuid4().hex[:8]}"
        topbar_id = f"{component_id}__bar"

        return dict(
            id=component_id,
            topbar_id=topbar_id,
            class_name=kwargs.class_name,
            sticky=normalize_bool(kwargs.sticky, default=True),
            bordered=normalize_bool(kwargs.bordered, default=True),
            shadow=normalize_enum(kwargs.shadow, ShadowSize, ShadowSize.NONE).value,
            aria_label=kwargs.aria_label,
            has_leading=bool(slots.get("leading")),
            has_title=bool(slots.get("title")),
            has_actions=bool(slots.get("actions")),
            slots=slots,
        )
