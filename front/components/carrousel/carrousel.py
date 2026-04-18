from typing import NamedTuple
from uuid import uuid4
from django_components import Component, register
from front.components.props import (
    AutoplayMode,
    ContentKind,
    DotsMode,
    normalize_bool,
    normalize_enum,
    normalize_int,
    normalize_kind,
)


@register("carrousel")
class CarrouselController(Component):
    template_file = "carrousel.html"
    css_file = "carrousel.css"
    js_file = "carrousel.js"

    class Kwargs(NamedTuple):
        id: str = ""
        class_name: str = ""
        kind: str = ContentKind.ARTICLE.value
        slides_per_view: int = 1
        slides_per_view_tablet: int | None = None
        slides_per_view_mobile: int | None = None
        gap: int = 16
        loop: bool = False
        show_controls: bool = True
        show_dots: bool = True
        dots_mode: str = DotsMode.AUTO.value
        autoplay_ms: int = 0
        autoplay_mode: str = AutoplayMode.STOP.value
        pause_on_hover: bool = True
        aria_label: str = "Carousel"
        prev_label: str = "Anterior"
        next_label: str = "Siguiente"
        prev_aria_label: str = "Previous page"
        next_aria_label: str = "Next page"

    def get_template_data(self, args, kwargs: Kwargs, slots, context) -> dict:
        kind = normalize_kind(kwargs.kind, default=ContentKind.ARTICLE).value
        component_id = kwargs.id or f"gc-carrousel-{uuid4().hex[:8]}"

        slides_per_view = normalize_int(kwargs.slides_per_view, default=1, minimum=1)
        slides_per_view_tablet = normalize_int(kwargs.slides_per_view_tablet, default=min(slides_per_view, 2), minimum=1)
        slides_per_view_mobile = normalize_int(kwargs.slides_per_view_mobile, default=1, minimum=1)
        gap = normalize_int(kwargs.gap, default=16, minimum=0)
        autoplay_ms = normalize_int(kwargs.autoplay_ms, default=0, minimum=0)
        dots_mode = normalize_enum(kwargs.dots_mode, DotsMode, DotsMode.AUTO).value

        return dict(
            id=component_id,
            class_name=kwargs.class_name,
            kind=kind,
            slides_per_view=slides_per_view,
            slides_per_view_tablet=slides_per_view_tablet,
            slides_per_view_mobile=slides_per_view_mobile,
            gap=gap,
            loop=normalize_bool(kwargs.loop),
            show_controls=normalize_bool(kwargs.show_controls, default=True),
            show_dots=normalize_bool(kwargs.show_dots, default=True),
            dots_mode=dots_mode,
            autoplay_ms=autoplay_ms,
            autoplay_mode=normalize_enum(kwargs.autoplay_mode, AutoplayMode, AutoplayMode.STOP).value,
            pause_on_hover=normalize_bool(kwargs.pause_on_hover, default=True),
            aria_label=kwargs.aria_label,
            status_label=f"{kwargs.aria_label} status",
            prev_label=kwargs.prev_label,
            next_label=kwargs.next_label,
            prev_aria_label=kwargs.prev_aria_label,
            next_aria_label=kwargs.next_aria_label,
            slots=slots,
        )
