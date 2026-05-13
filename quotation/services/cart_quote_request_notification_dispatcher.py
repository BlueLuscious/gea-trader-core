""" Notification dispatcher for public cart-to-quote conversions. """

import logging
from core.mail import TemplateMailService, TenantMailRecipientResolver
from quotation.models import QuoteModel
from quotation.services.cart_quote_request_notification_builder import CartQuoteRequestNotificationBuilder

logger = logging.getLogger(__name__)


class CartQuoteRequestNotificationDispatcher:
    """ Resolve recipients and dispatch quote-request notifications. """

    recipient_resolver_class = TenantMailRecipientResolver
    template_mail_service_class = TemplateMailService
    notification_builder_class = CartQuoteRequestNotificationBuilder

    @classmethod
    def send(cls, *, quote: QuoteModel) -> str | None:
        """ Notify the tenant about one newly created quote request.

        Args:
            quote: Newly created quote root.

        Returns:
            str | None: Celery task identifier when the notification was enqueued.
        """
        recipient = cls.recipient_resolver_class.resolve_contact_recipient(quote.tenant)
        if recipient is None:
            logger.warning(
                "Skipped public quote request notification because the tenant has no contact email quote_id=%s tenant_id=%s",
                quote.id,
                quote.tenant_id,
            )
            return None

        quote_items = list(quote.items.select_related("product", "variant").order_by("created_at", "id"))
        request = cls.notification_builder_class.build(
            quote=quote,
            quote_items=quote_items,
            recipient=recipient,
        )
        return cls.template_mail_service_class.send_async(request).id
