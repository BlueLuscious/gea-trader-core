from typing import NamedTuple
from django_components import Component, register
from front.components.props import ShadowSize, normalize_bool, normalize_enum


@register("topbar")
class TopbarController(Component):
    template_file = "topbar.html"
    css_file = "topbar.css"

    class Kwargs(NamedTuple):
        id: str = ""
        class_name: str = ""
        variant: str = "navbar"
        sticky: bool = False
        container: bool = True
        bordered: bool = True
        shadow: str = ShadowSize.NONE.value

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict:
        return dict(
            id=kwargs.id,
            class_name=kwargs.class_name,
            variant=kwargs.variant if kwargs.variant in {"navbar", "appbar"} else "navbar",
            sticky=normalize_bool(kwargs.sticky),
            container=normalize_bool(kwargs.container, default=True),
            bordered=normalize_bool(kwargs.bordered, default=True),
            shadow=normalize_enum(kwargs.shadow, ShadowSize, ShadowSize.NONE).value,
            slots=slots,
        )
