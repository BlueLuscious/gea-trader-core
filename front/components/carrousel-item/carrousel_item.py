from typing import NamedTuple
from django_components import Component, register


@register("carrousel_item")
class CarrouselItemController(Component):
    template_file = "carrousel-item.html"
    css_file = "carrousel-item.css"
    js_file = "carrousel-item.js"

    class Kwargs(NamedTuple):
        id: str = ""
        class_name: str = ""
        aria_label: str = ""

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict:
        return dict(
            id=kwargs.id,
            class_name=kwargs.class_name,
            aria_label=kwargs.aria_label,
            slots=slots,
        )
