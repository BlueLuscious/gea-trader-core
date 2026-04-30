""" Global toast runtime component. """

from typing import NamedTuple
from uuid import uuid4
from django_components import Component, register
from front.components.props import ToastPosition, normalize_enum


@register("toast")
class ToastComponent(Component):
    """ Render the global toast runtime root. """

    template_file = "toast.html"
    css_file = "toast.css"
    js_file = "toast.js"

    class Kwargs(NamedTuple):
        """ Typed kwargs accepted by the toast runtime root. """

        id: str = ""
        class_name: str = ""
        aria_label: str = "Notificaciones"
        max_visible: int = 4
        auto_close_ms: int = 4200
        position: str = ToastPosition.TOP_RIGHT.value

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict[str, object]:
        """ Build normalized template data for the toast root.

        Args:
            args: Positional component arguments.
            kwargs: Typed component keyword arguments.
            slots: Declared component slots.
            context: Ambient template context.

        Returns:
            dict[str, object]: Template data for the toast root.
        """
        component_id = kwargs.id or f"gc-toast-{uuid4().hex[:8]}"
        max_visible = kwargs.max_visible if kwargs.max_visible > 0 else 4
        auto_close_ms = kwargs.auto_close_ms if kwargs.auto_close_ms > 0 else 4200
        position = normalize_enum(kwargs.position, ToastPosition, ToastPosition.TOP_RIGHT).value
        return {
            "id": component_id,
            "class_name": kwargs.class_name,
            "aria_label": kwargs.aria_label,
            "max_visible": max_visible,
            "auto_close_ms": auto_close_ms,
            "position": position,
        }
