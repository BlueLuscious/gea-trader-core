""" Quote-request form renderer for public cart views. """

from django.http import HttpRequest
from django.template.loader import render_to_string
from front.forms import QuoteRequestForm


class QuoteRequestFormRenderer:
    """ Render the public quote-request form used by the shared cart modal. """

    def __init__(self, *, quote_modal_id: str = "site-quote-request-modal") -> None:
        """ Initialize the renderer with the target modal identifier.

        Args:
            quote_modal_id: DOM identifier used by modal close controls.
        """
        self.quote_modal_id = quote_modal_id

    def render(self, *, form: QuoteRequestForm | None = None, request: HttpRequest | None = None) -> str:
        """ Render the quote-request form HTML for modal usage.

        Args:
            form: Optional quote-request form instance.
            request: Optional current request used by Django template rendering.

        Returns:
            str: Server-rendered quote-request form markup.
        """
        return render_to_string(
            "cart/runtime/quote_request_form.html",
            {
                "form": form or QuoteRequestForm(),
                "quote_modal_id": self.quote_modal_id,
            },
            request=request,
        )
