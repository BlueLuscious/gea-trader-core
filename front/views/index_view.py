""" Public single-tenant home view for the front app. """

from front.views.base import PublicPageTemplateView
from front.views.mixins.pages import CatalogDataMixin, IndexPageContextMixin


class IndexView(IndexPageContextMixin, CatalogDataMixin, PublicPageTemplateView):
    """ Render the public single-tenant storefront home page. """

    template_name = "pages/index.html"
