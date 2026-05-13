""" Tests for the cart-to-quote converter. """

from cart.choices import CartStatus
from cart.models import CartItemModel, CartModel
from catalog.models import ProductModel, ProductVariantModel
from core.testing.base import LoggedTestCase
from masterdata.models import CategoryModel
from quotation.models import QuoteItemModel, QuoteModel
from quotation.services import CartQuoteRequestConverter
from tenancy.models import TenantModel


class TestCartQuoteRequestConverter(LoggedTestCase):
    """ Verify cart-to-quote persistence conversion behavior. """

    def setUp(self) -> None:
        """ Create one active cart with a catalog-backed line item. """
        self.tenant = TenantModel.objects.create(
            name="GEA Oils",
            slug="gea-oils-converter",
            business_email="info@geaoils.test",
            is_active=True,
        )
        category = CategoryModel.objects.create(
            tenant=self.tenant,
            name="Lubricants",
            slug="lubricants-converter",
            is_active=True,
        )
        product = ProductModel.objects.create(
            tenant=self.tenant,
            category=category,
            name="Hydraulic Oil 46",
            slug="hydraulic-oil-46-converter",
            is_active=True,
        )
        variant = ProductVariantModel.objects.create(
            product=product,
            name="205L Drum",
            sku="HYD-46-205L",
            is_default=True,
            is_active=True,
            price="98000.00",
        )
        self.cart = CartModel.objects.create(tenant=self.tenant, session_key="session-converter")
        CartItemModel.objects.create(cart=self.cart, product=product, variant=variant, quantity=2)

    def test_convert_persists_quote_snapshots_and_marks_cart_converted(self) -> None:
        """ Verify one active cart becomes a requested quote with snapshot items. """
        quote = CartQuoteRequestConverter.convert(
            cart=self.cart,
            customer_name="Ada Lovelace",
            customer_email="ada@example.com",
            customer_phone="+54 11 5555 0000",
            company_name="Analytical Engines",
            message="Need delivery timing.",
        )

        self.assertEqual(QuoteModel.objects.count(), 1)
        self.assertEqual(QuoteItemModel.objects.count(), 1)
        self.assertEqual(quote.workflow_status, "requested")
        self.assertEqual(quote.customer_name, "Ada Lovelace")
        self.assertEqual(quote.items.get().sku_snapshot, "HYD-46-205L")
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.status, CartStatus.CONVERTED)

    def test_convert_rejects_inactive_carts(self) -> None:
        """ Verify converted carts cannot be converted again. """
        self.cart.status = CartStatus.CONVERTED
        self.cart.save(update_fields=["status", "updated_at"])

        with self.assertRaisesMessage(ValueError, "Only active carts can be converted into quotes."):
            CartQuoteRequestConverter.convert(
                cart=self.cart,
                customer_name="Ada Lovelace",
                customer_email="ada@example.com",
                customer_phone="",
            )
