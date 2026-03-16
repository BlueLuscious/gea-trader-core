from typing import NamedTuple
from django_components import Component, register
from ..props import BadgeVariant, normalize_bool, normalize_enum


@register("card")
class CardController(Component):
    template_file = "card.html"
    css_file = "card.css"
    js_file = "card.js"

    class Kwargs(NamedTuple):
        id: str = ""
        href: str = ""
        class_name: str = ""
        elevated: bool = False
        clickable: bool = False
        badge_text: str = ""
        badge_variant: str = BadgeVariant.INVERSE.value
        header_divider: bool = False
        footer_divider: bool = False
        aria_label: str = ""

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict:
        return dict(
            id=kwargs.id,
            href=kwargs.href,
            class_name=kwargs.class_name,
            elevated=normalize_bool(kwargs.elevated),
            clickable=normalize_bool(kwargs.clickable),
            badge_text=kwargs.badge_text,
            badge_variant=normalize_enum(kwargs.badge_variant, BadgeVariant, BadgeVariant.INVERSE).value,
            header_divider=normalize_bool(kwargs.header_divider),
            footer_divider=normalize_bool(kwargs.footer_divider),
            aria_label=kwargs.aria_label,
            slots=slots,
        )
