""" Reusable modal component for runtime storefront dialogs. """

from typing import NamedTuple
from uuid import uuid4
from django_components import Component, register
from front.components.props import PanelWidth, normalize_bool, normalize_enum


@register("modal")
class ModalController(Component):
    """ Render one centered dialog shell with optional header and footer slots. """

    template_file = "modal.html"
    css_file = "modal.css"
    js_file = "modal.js"

    class Kwargs(NamedTuple):
        """ Typed kwargs accepted by the modal component. """

        id: str = ""
        class_name: str = ""
        width: str = PanelWidth.MD.value
        open: bool = False
        aria_label: str = "Diálogo modal"
        close_on_backdrop: bool = True
        close_on_escape: bool = True
        show_close_button: bool = True

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict[str, object]:
        """ Build normalized template data for the modal shell.

        Args:
            args: Positional component arguments.
            kwargs: Typed component keyword arguments.
            slots: Declared component slots.
            context: Ambient template context.

        Returns:
            dict[str, object]: Normalized template context for the modal shell.
        """
        component_id = kwargs.id or f"gc-modal-{uuid4().hex[:8]}"

        return {
            "id": component_id,
            "class_name": kwargs.class_name,
            "width": normalize_enum(kwargs.width, PanelWidth, PanelWidth.MD).value,
            "open": normalize_bool(kwargs.open),
            "aria_label": kwargs.aria_label,
            "close_on_backdrop": normalize_bool(kwargs.close_on_backdrop, default=True),
            "close_on_escape": normalize_bool(kwargs.close_on_escape, default=True),
            "show_close_button": normalize_bool(kwargs.show_close_button, default=True),
            "close_button_attrs": {"modal-close": "true"},
            "slots": slots,
        }
