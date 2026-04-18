from typing import NamedTuple
from django_components import Component, register
from front.components.props import IconStyle, normalize_bool, normalize_enum


@register("icon")
class IconController(Component):
    template_file = "icon.html"
    css_file = "icon.css"
    js_file = "icon.js"

    class Kwargs(NamedTuple):
        id: str = ""
        name: str = ""
        style: str = IconStyle.SOLID.value
        size: str = ""
        class_name: str = ""
        fixed_width: bool = False
        decorative: bool = True
        aria_label: str = ""

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict:
        style = normalize_enum(kwargs.style, IconStyle, IconStyle.SOLID).value
        icon_name = kwargs.name.removeprefix("fa-").strip()
        size = kwargs.size.removeprefix("fa-").strip()

        return dict(
            id=kwargs.id,
            style=style,
            icon_name=icon_name,
            size=size,
            class_name=kwargs.class_name,
            fixed_width=normalize_bool(kwargs.fixed_width),
            decorative=normalize_bool(kwargs.decorative, default=True),
            aria_label=kwargs.aria_label,
        )
