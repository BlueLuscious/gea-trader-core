""" Public JSON view that creates one quote request from the current cart. """

import logging
from django.http import HttpRequest, JsonResponse
from django.views import View
from front.forms import QuoteRequestForm
from front.views.cart.runtime import QuoteRequestFormRenderer
from quotation.services import CartQuoteRequestService
from .mixins import CartRuntimeViewMixin

logger = logging.getLogger(__name__)


class CartQuoteRequestView(CartRuntimeViewMixin, View):
    """ Validate and persist one public quote request from the current cart. """

    service_class = CartQuoteRequestService
    quote_request_form_renderer_class = QuoteRequestFormRenderer

    def get_quote_request_form_renderer(self) -> QuoteRequestFormRenderer:
        """ Return the renderer used for quote-request form fragments.

        Returns:
            QuoteRequestFormRenderer: Renderer for quote-request form markup.
        """
        return self.quote_request_form_renderer_class()

    def get(self, request: HttpRequest) -> JsonResponse:
        """ Return the rendered quote-request form for modal refreshes.

        Args:
            request: Current HTTP request.

        Returns:
            JsonResponse: Form refresh payload for the quote-request modal.
        """
        return JsonResponse(
            {
                "success": False,
                "form_html": self.get_quote_request_form_renderer().render(request=request),
            }
        )

    def post(self, request: HttpRequest) -> JsonResponse:
        """ Validate and persist one quote request from the active cart.

        Args:
            request: Current HTTP request.

        Returns:
            JsonResponse: Submission result with rendered HTML fragments.
        """
        tenant = self.get_tenant()
        cart = self.get_active_cart(request, tenant)
        form = QuoteRequestForm(request.POST)

        if cart is None or not cart.items.exists():
            form.add_error(None, "Tu carrito está vacío. Agregá productos antes de cotizar.")
            return JsonResponse(
                {
                    "success": False,
                    "form_html": self.get_quote_request_form_renderer().render(
                        form=form,
                        request=request,
                    ),
                }
            )

        if not form.is_valid():
            return JsonResponse(
                {
                    "success": False,
                    "form_html": self.get_quote_request_form_renderer().render(
                        form=form,
                        request=request,
                    ),
                }
            )

        try:
            result = self.service_class.create_from_cart(
                cart=cart,
                customer_name=form.cleaned_data["customer_name"],
                customer_email=form.cleaned_data["customer_email"],
                customer_phone=form.cleaned_data["customer_phone"],
                company_name=form.cleaned_data["company_name"],
                message=form.cleaned_data["message"],
            )
        except ValueError as error:
            form.add_error(None, str(error))
            return JsonResponse(
                {
                    "success": False,
                    "form_html": self.get_quote_request_form_renderer().render(
                        form=form,
                        request=request,
                    ),
                }
            )

        logger.info(
            "Accepted public quote request quote_id=%s notification_task_id=%s",
            result.quote.id,
            result.notification_task_id,
        )
        active_cart = self.get_active_cart(request, tenant)
        return JsonResponse(
            {
                "success": True,
                "quote_id": result.quote.id,
                "message": self.build_success_message(customer_name=result.quote.customer_name),
                "cart_state": self.build_cart_state(active_cart),
            }
        )

    def build_success_message(self, *, customer_name: str) -> str:
        """ Build the public quote-request success copy.

        Args:
            customer_name: Customer name used in the success copy.

        Returns:
            str: Success copy shown in the toast.
        """
        if customer_name:
            return f"Gracias, {customer_name}. Recibimos tu pedido y te vamos a contactar a la brevedad."

        return "Recibimos tu pedido y te vamos a contactar a la brevedad."
