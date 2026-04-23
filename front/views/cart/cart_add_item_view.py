""" Public JSON view that adds one item to the current cart. """

from django.http import HttpRequest, JsonResponse
from django.views import View
from cart.models import CartItemModel
from .mixins import CartRuntimeViewMixin


class CartAddItemView(CartRuntimeViewMixin, View):
    """ Add one product or variant selection to the persisted cart. """

    def post(self, request: HttpRequest) -> JsonResponse:
        """ Persist one incoming cart selection and return the next cart state.

        Args:
            request: Current HTTP request.

        Returns:
            JsonResponse: Serialized updated cart state.
        """
        tenant = self.get_tenant()
        payload = self.get_request_payload(request)
        product = self.get_product(tenant, payload.get("product_id"))
        if product is None:
            return self.build_error_response("Selected product is no longer available.", status=404)

        variant = self.get_variant(product, payload.get("variant_id"))
        quantity = max(int(payload.get("quantity") or 1), 1)
        cart = self.get_or_create_active_cart(request, tenant)
        item, created = CartItemModel.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={"quantity": quantity},
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity", "updated_at"])

        return JsonResponse(self.build_cart_state(cart))
