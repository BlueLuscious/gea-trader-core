""" Cart-to-quote conversion service for public quote requests. """

from django.db import transaction
from cart.choices import CartStatus
from cart.models import CartItemModel, CartModel
from quotation.choices import QuoteWorkflowStatus
from quotation.factories import QuoteItemSnapshotFactory
from quotation.models import QuoteItemModel, QuoteModel


class CartQuoteRequestConverter:
    """ Convert one active runtime cart into persisted quote snapshots. """

    quote_item_snapshot_factory_class = QuoteItemSnapshotFactory

    @classmethod
    def convert(
        cls,
        *,
        cart: CartModel,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        company_name: str = "",
        message: str = "",
    ) -> QuoteModel:
        """ Convert one active cart into a requested quote.

        Args:
            cart: Active runtime cart selected by the storefront visitor.
            customer_name: Customer display name.
            customer_email: Optional customer email.
            customer_phone: Optional customer phone number.
            company_name: Optional company name.
            message: Optional free-text customer message.

        Returns:
            QuoteModel: Created persisted quote.

        Raises:
            ValueError: When the cart is not active or contains no items.
        """
        if cart.status != CartStatus.ACTIVE:
            raise ValueError("Only active carts can be converted into quotes.")

        cart_items = cls.get_cart_items(cart=cart)
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

        return quote

    @staticmethod
    def get_cart_items(*, cart: CartModel) -> list[CartItemModel]:
        """ Return cart items in the conversion snapshot order.

        Args:
            cart: Runtime cart selected for quote conversion.

        Returns:
            list[CartItemModel]: Catalog-loaded cart items.
        """
        return list(CartItemModel.objects.for_cart(cart).with_catalog().order_by("created_at", "id"))
