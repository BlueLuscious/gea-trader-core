""" Notification request builder for public cart-to-quote conversions. """

from decimal import Decimal
from core.mail import TemplateMailRequestDTO, TenantMailReplyPolicy
from quotation.models import QuoteItemModel, QuoteModel
from quotation.services.quote_admin_url_builder import QuoteAdminUrlBuilder


class CartQuoteRequestNotificationBuilder:
    """ Build tenant notification requests for public quote submissions. """

    reply_policy_class = TenantMailReplyPolicy
    quote_admin_url_builder_class = QuoteAdminUrlBuilder

    @classmethod
    def build(cls, *, quote: QuoteModel, quote_items: list[QuoteItemModel], recipient: str) -> TemplateMailRequestDTO:
        """ Build one tenant notification request for a created quote.

        Args:
            quote: Newly created quote root.
            quote_items: Persisted quote-item snapshots.
            recipient: Tenant recipient email address.

        Returns:
            TemplateMailRequestDTO: Prepared tenant notification request.
        """
        subject_customer = quote.customer_name or quote.company_name or f"Cotización {quote.id}"
        return TemplateMailRequestDTO(
            subject=f"Nueva solicitud de cotización de {subject_customer}",
            to=[recipient],
            context=cls.build_mail_context(quote=quote, quote_items=quote_items),
            html_template_name="quotation/mail/messages/cart_quote_request_notification.html",
            text_template_name="quotation/mail/messages/cart_quote_request_notification.txt",
            tenant=quote.tenant,
            reply_to=cls.reply_policy_class.resolve_customer_reply_to(quote.customer_email),
        )

    @classmethod
    def build_mail_context(cls, *, quote: QuoteModel, quote_items: list[QuoteItemModel]) -> dict[str, object]:
        """ Build the templated mail context for one quote request.

        Args:
            quote: Newly created quote root.
            quote_items: Persisted quote-item snapshots.

        Returns:
            dict[str, object]: Template context for notification mail.
        """
        subtotal = sum(
            (item.unit_price_snapshot or Decimal("0")) * item.quantity
            for item in quote_items
            if item.unit_price_snapshot is not None
        )
        return {
            "mail_title": "Nueva solicitud de cotización",
            "mail_intro": "Se recibió una nueva solicitud desde el sitio público y ya quedó registrada para seguimiento comercial.",
            "mail_outro": "Podés revisar la cotización en el panel de administración para continuar la conversación con el cliente.",
            "cta_label": "Abrir cotización en admin",
            "cta_url": cls.quote_admin_url_builder_class.build(quote=quote),
            "quote_id": quote.id,
            "quote_customer_name": quote.customer_name,
            "quote_customer_email": quote.customer_email,
            "quote_customer_phone": quote.customer_phone,
            "quote_company_name": quote.company_name,
            "quote_notes": quote.notes,
            "quote_items": [
                {
                    "product_name_snapshot": item.product_name_snapshot,
                    "sku_snapshot": item.sku_snapshot,
                    "quantity": item.quantity,
                    "unit_price_snapshot": str(item.unit_price_snapshot) if item.unit_price_snapshot is not None else "",
                }
                for item in quote_items
            ],
            "quote_item_count": len(quote_items),
            "quote_subtotal_text": f"ARS {subtotal:.2f}" if subtotal else "",
        }
