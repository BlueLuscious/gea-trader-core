""" Public service that converts one cart into a persisted quote request. """

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Optional
from urllib.parse import urljoin

from django.conf import settings
from django.db import transaction
from django.urls import reverse

from cart.choices import CartStatus
from cart.models import CartItemModel, CartModel
from core.mail import TemplateMailRequestDTO, TemplateMailService, TenantMailRecipientResolver, TenantMailReplyPolicy
from quotation.choices import QuoteWorkflowStatus
from quotation.dtos import CartQuoteRequestResultDTO
from quotation.dtos.factories import CartQuoteRequestResultDTOFactory
from quotation.models import QuoteItemModel, QuoteModel


logger = logging.getLogger(__name__)


class CartQuoteRequestService:
    """ Convert one active cart into a requested quote and notify the tenant. """

    recipient_resolver_class = TenantMailRecipientResolver
    reply_policy_class = TenantMailReplyPolicy
    template_mail_service_class = TemplateMailService
    result_factory_class = CartQuoteRequestResultDTOFactory

    @classmethod
    def create_from_cart(
        cls,
        *,
        cart: CartModel,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        company_name: str = "",
        message: str = "",
    ) -> CartQuoteRequestResultDTO:
        """ Convert one active cart into a persisted quote request.

        Args:
            cart: Active runtime cart selected by the storefront visitor.
            customer_name: Customer display name.
            customer_email: Optional customer email.
            customer_phone: Optional customer phone number.
            company_name: Optional company name.
            message: Optional free-text customer message.

        Returns:
            CartQuoteRequestResultDTO: Created quote and notification result.

        Raises:
            ValueError: When the cart is not active or contains no items.
        """
        if cart.status != CartStatus.ACTIVE:
            raise ValueError("Only active carts can be converted into quotes.")

        cart_items = list(CartItemModel.objects.for_cart(cart).with_catalog().order_by("created_at", "id"))
        if not cart_items:
            raise ValueError("A quote request requires at least one cart item.")

        with transaction.atomic():
            quote = QuoteModel.objects.create(
                tenant=cart.tenant,
                cart=cart,
                user=cart.user,
                workflow_status=QuoteWorkflowStatus.REQUESTED,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                company_name=company_name,
                notes=message,
            )
            quote_items = [cls._build_quote_item(quote=quote, cart_item=cart_item) for cart_item in cart_items]
            QuoteItemModel.objects.bulk_create(quote_items)
            cart.status = CartStatus.CONVERTED
            cart.save(update_fields=["status", "updated_at"])

        notification_task_id = cls._send_notification(quote=quote)
        logger.info(
            "Created public quote request quote_id=%s cart_id=%s item_count=%s notification_task_id=%s",
            quote.id,
            cart.id,
            len(cart_items),
            notification_task_id,
        )
        return cls.result_factory_class.build(
            quote=quote,
            notification_task_id=notification_task_id,
        )

    @staticmethod
    def _build_quote_item(*, quote: QuoteModel, cart_item: CartItemModel) -> QuoteItemModel:
        """ Build one quote-item snapshot from one cart item.

        Args:
            quote: Newly created quote root.
            cart_item: Runtime cart item to snapshot.

        Returns:
            QuoteItemModel: Unsaved quote-item snapshot.
        """
        product = cart_item.product
        variant = cart_item.variant
        unit_price = variant.price if variant is not None else product.get_public_price()
        return QuoteItemModel(
            quote=quote,
            product=product,
            variant=variant,
            product_name_snapshot=product.name,
            sku_snapshot=variant.sku if variant is not None else product.sku_base,
            attributes_snapshot=dict(variant.attributes_json or {}) if variant is not None else {},
            unit_price_snapshot=unit_price,
            quantity=cart_item.quantity,
            notes=cart_item.notes,
        )

    @classmethod
    def _send_notification(cls, *, quote: QuoteModel) -> Optional[str]:
        """ Notify the tenant about one newly created quote request.

        Args:
            quote: Newly created quote root.

        Returns:
            Optional[str]: Celery task identifier when the notification was enqueued.
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
        subject_customer = quote.customer_name or quote.company_name or f"Cotización {quote.id}"
        request = TemplateMailRequestDTO(
            subject=f"Nueva solicitud de cotización de {subject_customer}",
            to=[recipient],
            context=cls._build_mail_context(quote=quote, quote_items=quote_items),
            html_template_name="quotation/mail/messages/cart_quote_request_notification.html",
            text_template_name="quotation/mail/messages/cart_quote_request_notification.txt",
            tenant=quote.tenant,
            reply_to=cls.reply_policy_class.resolve_customer_reply_to(quote.customer_email),
        )
        return cls.template_mail_service_class.send_async(request).id

    @classmethod
    def _build_mail_context(cls, *, quote: QuoteModel, quote_items: list[QuoteItemModel]) -> dict[str, object]:
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
            "cta_url": cls._build_quote_admin_url(quote),
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

    @classmethod
    def _build_quote_admin_url(cls, quote: QuoteModel) -> str:
        """ Build one owner-admin URL for the created quote.

        Args:
            quote: Newly created quote root.

        Returns:
            str: Absolute owner-admin URL when one base URL exists, otherwise one relative path.
        """
        admin_path = reverse("owner_admin:quotation_quotemodel_change", args=[quote.id])
        base_url_setting = str(getattr(settings, "BASE_URL", "") or "").strip()
        website_url = str(getattr(quote.tenant, "website_url", "") or "").strip()
        base_url = base_url_setting or website_url
        if not base_url:
            return admin_path

        return urljoin(f"{base_url.rstrip('/')}/", admin_path.lstrip("/"))
