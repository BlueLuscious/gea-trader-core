""" Tests for the cart-to-quote request service. """

from django.core import mail
from django.test import override_settings

from cart.models import CartItemModel, CartModel
from catalog.models import ProductModel, ProductVariantModel
from core.testing.base import LoggedTestCase
from masterdata.models import CategoryModel
from quotation.models import QuoteItemModel, QuoteModel
from quotation.services import CartQuoteRequestService
from tenancy.models import TenantModel


class TestCartQuoteRequestService(LoggedTestCase):
    """ Verify cart conversion into quote requests stays tenant-safe and complete. """

    def setUp(self) -> None:
        """ Create one tenant, catalog product, cart, and cart item for the service flow. """
        self.tenant = TenantModel.objects.create(
            name="GEA Oils",
            slug="gea-oils",
            business_email="info@geaoils.test",
            is_active=True,
        )
        category = CategoryModel.objects.create(
            tenant=self.tenant,
            name="Lubricants",
            slug="lubricants",
            is_active=True,
        )
        product = ProductModel.objects.create(
            tenant=self.tenant,
            category=category,
            name="Hydraulic Oil 46",
            slug="hydraulic-oil-46",
            is_active=True,
            requires_quote=False,
        )
        variant = ProductVariantModel.objects.create(
            product=product,
            name="205L Drum",
            sku="HYD-46-205L",
            is_default=True,
            is_active=True,
            price="98000.00",
        )
        self.cart = CartModel.objects.create(tenant=self.tenant, session_key="session-123")
        CartItemModel.objects.create(cart=self.cart, product=product, variant=variant, quantity=2)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
        BASE_URL="https://owner.geatrader.test",
    )
    def test_create_from_cart_builds_quote_snapshots_and_sends_notification(self) -> None:
        """ Verify one active cart becomes a requested quote with one outbound tenant notification. """
        result = CartQuoteRequestService.create_from_cart(
            cart=self.cart,
            customer_name="Ada Lovelace",
            customer_email="ada@example.com",
            customer_phone="+54 11 5555 0000",
            company_name="Analytical Engines",
            message="Necesito disponibilidad y plazo de entrega.",
        )

        self.assertEqual(QuoteModel.objects.count(), 1)
        self.assertEqual(QuoteItemModel.objects.count(), 1)
        self.assertEqual(result.quote.workflow_status, "requested")
        self.assertTrue(result.notification_task_id)
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.status, "converted")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Correo:", mail.outbox[0].body)
        self.assertIn("Productos solicitados:", mail.outbox[0].body)
        self.assertIn(
            f"https://owner.geatrader.test/owner-admin/quotation/quotemodel/{result.quote.id}/change/",
            mail.outbox[0].alternatives[0][0],
        )

    def test_create_from_cart_rejects_empty_carts(self) -> None:
        """ Verify one quote request cannot be created from an empty cart. """
        empty_cart = CartModel.objects.create(tenant=self.tenant, session_key="session-empty")

        with self.assertRaisesMessage(ValueError, "A quote request requires at least one cart item."):
            CartQuoteRequestService.create_from_cart(
                cart=empty_cart,
                customer_name="Ada Lovelace",
                customer_email="ada@example.com",
                customer_phone="",
            )
