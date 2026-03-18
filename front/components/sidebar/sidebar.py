from typing import NamedTuple
from uuid import uuid4
from django_components import Component, register
from front.components.props import PanelWidth, normalize_bool, normalize_enum


@register("sidebar")
class SidebarController(Component):
    template_file = "sidebar.html"
    css_file = "sidebar.css"
    js_file = "sidebar.js"

    class Kwargs(NamedTuple):
        id: str = ""
        class_name: str = ""
        side: str = "right"
        width: str = PanelWidth.MD.value
        open: bool = False
        aria_label: str = "Panel lateral"
        close_on_backdrop: bool = True
        close_on_escape: bool = True
        show_close_button: bool = True

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict:
        component_id = kwargs.id or f"gc-sidebar-{uuid4().hex[:8]}"

        return dict(
            id=component_id,
            class_name=kwargs.class_name,
            side=kwargs.side if kwargs.side in {"left", "right"} else "right",
            width=normalize_enum(kwargs.width, PanelWidth, PanelWidth.MD).value,
            open=normalize_bool(kwargs.open),
            aria_label=kwargs.aria_label,
            close_on_backdrop=normalize_bool(kwargs.close_on_backdrop, default=True),
            close_on_escape=normalize_bool(kwargs.close_on_escape, default=True),
            show_close_button=normalize_bool(kwargs.show_close_button, default=True),
            close_button_attrs={"sidebar-close": "true"},
            slots=slots,
        )
