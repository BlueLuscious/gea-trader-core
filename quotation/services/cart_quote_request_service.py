""" Public service that converts one cart into a persisted quote request. """

import logging
from django.db import transaction
from cart.choices import CartStatus
from cart.models import CartItemModel, CartModel
from core.mail import TemplateMailService, TenantMailRecipientResolver
from quotation.choices import QuoteWorkflowStatus
from quotation.dtos import CartQuoteRequestResultDTO
from quotation.dtos.factories import CartQuoteRequestResultDTOFactory
from quotation.factories import QuoteItemSnapshotFactory
from quotation.models import QuoteItemModel, QuoteModel
from quotation.services.cart_quote_request_notification_builder import CartQuoteRequestNotificationBuilder

logger = logging.getLogger(__name__)


class CartQuoteRequestService:
    """ Convert one active cart into a requested quote and notify the tenant. """

    recipient_resolver_class = TenantMailRecipientResolver
    template_mail_service_class = TemplateMailService
    result_factory_class = CartQuoteRequestResultDTOFactory
    notification_builder_class = CartQuoteRequestNotificationBuilder
    quote_item_snapshot_factory_class = QuoteItemSnapshotFactory

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
            quote_items = [
                cls.quote_item_snapshot_factory_class.build(quote=quote, cart_item=cart_item)
                for cart_item in cart_items
            ]
            QuoteItemModel.objects.bulk_create(quote_items)
            cart.status = CartStatus.CONVERTED
            cart.save(update_fields=["status", "updated_at"])

        notification_task_id = cls.send_notification(quote=quote)
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

    @classmethod
    def send_notification(cls, *, quote: QuoteModel) -> str | None:
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
