""" Public single-tenant home view for the front app. """

from django.views.generic import TemplateView
from front.views.mixins.pages import CatalogPresentationMixin, IndexPageContextMixin, TenantAwareMixin


class IndexView(IndexPageContextMixin, CatalogPresentationMixin, TenantAwareMixin, TemplateView):
    """ Render the public single-tenant storefront home page. """

    template_name = "pages/index.html"
