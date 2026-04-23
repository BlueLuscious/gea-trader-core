""" Public JSON view that updates one cart-item quantity. """

from django.http import HttpRequest, JsonResponse
from django.views import View
from .mixins import CartRuntimeViewMixin


class CartUpdateQuantityView(CartRuntimeViewMixin, View):
    """ Update one persisted cart-item quantity. """

    def post(self, request: HttpRequest) -> JsonResponse:
        """ Persist one new quantity and return the next cart state.

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

        quantity = int(payload.get("quantity") or 0)
        if quantity <= 0:
            item.delete()
        else:
            item.quantity = quantity
            item.save(update_fields=["quantity", "updated_at"])

        return JsonResponse(self.build_cart_state(cart))
