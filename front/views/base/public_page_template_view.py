""" Base template view for public storefront pages. """

from django.views.generic import TemplateView
from front.views.cart.mixins import QuoteRequestModalContextMixin
from front.views.mixins.base import LayoutContextMixin


class PublicPageTemplateView(QuoteRequestModalContextMixin, LayoutContextMixin, TemplateView):
    """ Provide shared public-page layout and quote-modal context for template views. """
