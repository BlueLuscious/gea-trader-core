from typing import NamedTuple
from uuid import uuid4
from django_components import Component, register
from front.components.props import Size, normalize_bool, normalize_enum


@register("collapsible")
class CollapsibleController(Component):
    template_file = "collapsible.html"
    css_file = "collapsible.css"
    js_file = "collapsible.js"

    class Kwargs(NamedTuple):
        id: str = ""
        class_name: str = ""
        summary_class_name: str = ""
        panel_class_name: str = ""
        size: str = Size.MD.value
        panel_width: str = "md"
        open: bool = False
        aria_label: str = ""
        close_on_outside: bool = False
        close_on_escape: bool = True
        close_on_link_click: bool = False

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict:
        component_id = kwargs.id or f"gc-collapsible-{uuid4().hex[:8]}"
        panel_id = f"{component_id}__panel"

        return dict(
            id=component_id,
            panel_id=panel_id,
            class_name=kwargs.class_name,
            summary_class_name=kwargs.summary_class_name,
            panel_class_name=kwargs.panel_class_name,
            size=normalize_enum(kwargs.size, Size, Size.MD).value,
            panel_width=kwargs.panel_width if kwargs.panel_width in {"auto", "sm", "md", "lg", "xl", "full"} else "md",
            open=normalize_bool(kwargs.open),
            aria_label=kwargs.aria_label,
            close_on_outside=normalize_bool(kwargs.close_on_outside),
            close_on_escape=normalize_bool(kwargs.close_on_escape, default=True),
            close_on_link_click=normalize_bool(kwargs.close_on_link_click),
            slots=slots,
        )
