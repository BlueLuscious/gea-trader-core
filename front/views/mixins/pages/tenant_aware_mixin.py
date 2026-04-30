""" Composed tenant-aware storefront mixin for public pages. """

from front.views.cart.mixins.quote_request_modal_context_mixin import QuoteRequestModalContextMixin
from front.views.mixins.base.layout_context_mixin import LayoutContextMixin


class TenantAwareMixin(QuoteRequestModalContextMixin, LayoutContextMixin):
    """ Compose shared layout and quote-request modal context for public storefront pages. """
