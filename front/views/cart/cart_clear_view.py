""" Public JSON view that clears the active cart. """

from django.http import HttpRequest, JsonResponse
from django.views import View
from cart.models import CartItemModel
from .mixins import CartRuntimeViewMixin


class CartClearView(CartRuntimeViewMixin, View):
    """ Clear all persisted items from the active cart. """

    def post(self, request: HttpRequest) -> JsonResponse:
        """ Remove all active cart items and return the empty cart state.

        Args:
            request: Current HTTP request.

        Returns:
            JsonResponse: Serialized updated cart state.
        """
        tenant = self.get_tenant()
        cart = self.get_active_cart(request, tenant)
        if cart is None:
            return JsonResponse(self.build_cart_state(None))

        CartItemModel.objects.for_cart(cart).delete()
        return JsonResponse(self.build_cart_state(cart))
