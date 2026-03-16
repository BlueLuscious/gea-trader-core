from typing import NamedTuple
from django_components import Component, register
from front.components.props import BadgeVariant, ShadowSize, normalize_bool, normalize_enum


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
        shadow: str = ""
        aria_label: str = ""

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict:
        shadow = kwargs.shadow
        if not shadow:
            shadow = ShadowSize.MD.value if normalize_bool(kwargs.elevated) else ShadowSize.SM.value

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
            shadow=normalize_enum(shadow, ShadowSize, ShadowSize.SM).value,
            aria_label=kwargs.aria_label,
            slots=slots,
        )
