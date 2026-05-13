""" Public service that converts one cart into a persisted quote request. """

import logging
from cart.models import CartModel
from quotation.dtos import CartQuoteRequestResultDTO
from quotation.dtos.factories import CartQuoteRequestResultDTOFactory
from quotation.services.cart_quote_request_converter import CartQuoteRequestConverter
from quotation.services.cart_quote_request_notification_dispatcher import CartQuoteRequestNotificationDispatcher

logger = logging.getLogger(__name__)


class CartQuoteRequestService:
    """ Convert one active cart into a requested quote and notify the tenant. """

    converter_class = CartQuoteRequestConverter
    notification_dispatcher_class = CartQuoteRequestNotificationDispatcher
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
        quote = cls.converter_class.convert(
            cart=cart,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            company_name=company_name,
            message=message,
        )
        notification_task_id = cls.notification_dispatcher_class.send(quote=quote)
        item_count = quote.items.count()
        logger.info(
            "Created public quote request quote_id=%s cart_id=%s item_count=%s notification_task_id=%s",
            quote.id,
            cart.id,
            item_count,
            notification_task_id,
        )
        return cls.result_factory_class.build(
            quote=quote,
            notification_task_id=notification_task_id,
        )
