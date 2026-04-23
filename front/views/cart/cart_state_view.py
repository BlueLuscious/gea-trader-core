""" Public JSON view that exposes the current cart state. """

from django.http import HttpRequest, JsonResponse
from django.views import View
from .mixins import CartRuntimeViewMixin


class CartStateView(CartRuntimeViewMixin, View):
    """ Return the current persisted public cart state. """

    def get(self, request: HttpRequest) -> JsonResponse:
        """ Return one serialized active cart state.

        Args:
            request: Current HTTP request.

        Returns:
            JsonResponse: Serialized cart state.
        """
        tenant = self.get_tenant()
        cart = self.get_active_cart(request, tenant)
        return JsonResponse(self.build_cart_state(cart))
