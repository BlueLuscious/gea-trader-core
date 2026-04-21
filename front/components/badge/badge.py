from typing import NamedTuple
from django_components import Component, register
from front.components.props import BadgeSize, BadgeVariant, normalize_enum


@register("badge")
class BadgeController(Component):
    """ Render a compact status or label badge. """

    template_file = "badge.html"
    css_file = "badge.css"
    js_file = "badge.js"

    class Kwargs(NamedTuple):
        id: str = ""
        label: str = ""
        variant: str = BadgeVariant.NEUTRAL.value
        size: str = BadgeSize.MD.value
        class_name: str = ""
        aria_label: str = ""

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict:
        """ Normalize badge props before rendering.

        Args:
            args: Positional component args.
            kwargs: Typed keyword arguments passed into the component.
            slots: Component slot registry.
            context: Parent render context.

        Returns:
            dict: Normalized template data for the badge.
        """
        variant = normalize_enum(kwargs.variant, BadgeVariant, BadgeVariant.NEUTRAL).value
        size = normalize_enum(kwargs.size, BadgeSize, BadgeSize.MD).value

        return dict(
            id=kwargs.id,
            label=kwargs.label,
            variant=variant,
            size=size,
            class_name=kwargs.class_name,
            aria_label=kwargs.aria_label,
        )
