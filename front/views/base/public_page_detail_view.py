""" Base detail view for public storefront pages. """

from django.views.generic import DetailView
from front.views.cart.mixins import QuoteRequestModalContextMixin
from front.views.mixins.base import LayoutContextMixin


class PublicPageDetailView(QuoteRequestModalContextMixin, LayoutContextMixin, DetailView):
    """ Provide shared public-page layout and quote-modal context for detail views. """
