from typing import NamedTuple
from django_components import Component, register
from front.components.props import BadgeVariant, normalize_enum


@register("badge")
class BadgeController(Component):
    template_file = "badge.html"
    css_file = "badge.css"
    js_file = "badge.js"

    class Kwargs(NamedTuple):
        id: str = ""
        label: str = ""
        variant: str = BadgeVariant.NEUTRAL.value
        class_name: str = ""
        aria_label: str = ""

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict:
        variant = normalize_enum(kwargs.variant, BadgeVariant, BadgeVariant.NEUTRAL).value

        return dict(
            id=kwargs.id,
            label=kwargs.label,
            variant=variant,
            class_name=kwargs.class_name,
            aria_label=kwargs.aria_label,
        )
