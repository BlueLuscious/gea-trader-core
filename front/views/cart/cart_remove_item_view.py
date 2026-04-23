""" Public JSON view that removes one cart item. """

from django.http import HttpRequest, JsonResponse
from django.views import View
from .mixins import CartRuntimeViewMixin


class CartRemoveItemView(CartRuntimeViewMixin, View):
    """ Remove one persisted cart item from the active cart. """

    def post(self, request: HttpRequest) -> JsonResponse:
        """ Remove one item and return the next cart state.

        Args:
            request: Current HTTP request.

        Returns:
            JsonResponse: Serialized updated cart state.
        """
        tenant = self.get_tenant()
        cart = self.get_active_cart(request, tenant)
        if cart is None:
            return JsonResponse(self.build_cart_state(None))

        payload = self.get_request_payload(request)
        item = self.get_cart_item(cart, payload.get("item_id"))
        if item is None:
            return self.build_error_response("Selected cart item no longer exists.", status=404)

        item.delete()
        return JsonResponse(self.build_cart_state(cart))
