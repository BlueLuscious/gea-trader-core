from typing import NamedTuple
from uuid import uuid4
from django_components import Component, register, Slot
from front.components.props import ShadowSize, normalize_bool, normalize_enum


@register("navbar")
class NavbarController(Component):
    template_file = "navbar.html"
    css_file = "navbar.css"

    class Kwargs(NamedTuple):
        id: str = ""
        class_name: str = ""
        sticky: bool = True
        bordered: bool = True
        shadow: str = ShadowSize.NONE.value
        links_position: str = "center"
        aria_label: str = "Navegacion principal"
        menu_aria_label: str = "Abrir menu"

    def get_template_data(self, args, kwargs: Kwargs, slots: dict[str, Slot], context) -> dict:
        component_id = kwargs.id or f"gc-navbar-{uuid4().hex[:8]}"
        topbar_id = f"{component_id}__bar"
        menu_id = f"{component_id}__menu"

        return dict(
            id=component_id,
            topbar_id=topbar_id,
            menu_id=menu_id,
            class_name=kwargs.class_name,
            sticky=normalize_bool(kwargs.sticky, default=True),
            bordered=normalize_bool(kwargs.bordered, default=True),
            shadow=normalize_enum(kwargs.shadow, ShadowSize, ShadowSize.NONE).value,
            links_position=kwargs.links_position if kwargs.links_position in {"center", "end"} else "center",
            aria_label=kwargs.aria_label,
            menu_aria_label=kwargs.menu_aria_label,
            has_brand=bool(slots.get("brand")),
            has_links=bool(slots.get("links")),
            has_actions=bool(slots.get("actions")),
            slots=slots,
        )
