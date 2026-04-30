""" Quote-request modal context helpers for public storefront pages. """

from django.template.loader import render_to_string
from front.forms import QuoteRequestForm


class QuoteRequestModalContextMixin:
    """ Provide the shared quote-request modal context for storefront pages. """

    quote_modal_id = "site-quote-request-modal"

    def build_quote_request_modal_context(self) -> dict[str, str]:
        """ Build the shared quote-request modal context for the base layout.

        Returns:
            dict[str, str]: Modal identifier and server-rendered form HTML.
        """
        return {
            "site_quote_request_modal_id": self.quote_modal_id,
            "site_quote_request_form_html": self.render_quote_request_form_html(),
        }

    def render_quote_request_form_html(self) -> str:
        """ Render the initial quote-request form HTML for the shared modal.

        Returns:
            str: Server-rendered quote-request form markup.
        """
        return render_to_string(
            "cart/runtime/quote_request_form.html",
            {
                "form": QuoteRequestForm(),
                "quote_modal_id": self.quote_modal_id,
            },
            request=self.request,
        )

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """ Extend context with the shared quote-request modal data.

        Args:
            **kwargs: Generic view context keyword arguments.

        Returns:
            dict[str, object]: Context extended with quote-request modal data.
        """
        context = super().get_context_data(**kwargs)
        context.update(self.build_quote_request_modal_context())
        return context
