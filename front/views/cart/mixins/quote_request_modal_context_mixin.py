""" Quote-request modal context helpers for public storefront pages. """

from front.views.cart.runtime import QuoteRequestFormRenderer


class QuoteRequestModalContextMixin:
    """ Provide the shared quote-request modal context for storefront pages. """

    quote_modal_id = "site-quote-request-modal"
    quote_request_form_renderer_class = QuoteRequestFormRenderer

    def get_quote_request_form_renderer(self) -> QuoteRequestFormRenderer:
        """ Return the renderer used for the quote-request modal form.

        Returns:
            QuoteRequestFormRenderer: Renderer for the quote-request form.
        """
        return self.quote_request_form_renderer_class()

    def render_quote_request_form_html(self) -> str:
        """ Render the initial quote-request form HTML for the shared modal.

        Returns:
            str: Server-rendered quote-request form markup.
        """
        return self.get_quote_request_form_renderer().render(request=self.request)

    def build_quote_request_modal_context(self) -> dict[str, str]:
        """ Build the shared quote-request modal context for the base layout.

        Returns:
            dict[str, str]: Modal identifier and server-rendered form HTML.
        """
        return {
            "site_quote_request_modal_id": self.quote_modal_id,
            "site_quote_request_form_html": self.render_quote_request_form_html(),
        }

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """ Extend context with the shared quote-request modal data.

        Args:
            **kwargs: Generic view context keyword arguments.

        Returns:
            dict[str, object]: Context extended with quote-request modal data.
        """
        context: dict[str, object] = super().get_context_data(**kwargs)
        context.update(self.build_quote_request_modal_context())
        return context
