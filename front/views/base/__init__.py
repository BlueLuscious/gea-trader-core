""" Public front base view exports. """

from front.views.base.public_page_detail_view import PublicPageDetailView
from front.views.base.public_page_template_view import PublicPageTemplateView

__all__: list[str] = [
    "PublicPageDetailView",
    "PublicPageTemplateView",
]
