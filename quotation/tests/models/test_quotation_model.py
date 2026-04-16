from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils.translation import override
from core.testing.base import LoggedTestCase
from cart.models import CartModel
from catalog.models import ProductModel, ProductVariantModel
from tenancy.models import TenantModel
from quotation.models import QuoteItemModel, QuoteModel


class TestQuotationModel(LoggedTestCase):
    """ Cover quotation model behavior. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for catalog-linked quotation fixtures.

        Args:
            slug: Stable tenant slug.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_quote_and_snapshot_item_relationships(self) -> None:
        """ Verify quote and quote item relationships persist correctly. """
        tenant = self._create_tenant("quotation-model")
        cart = CartModel.objects.create(tenant=tenant, session_key='session-quote')
        product = ProductModel.objects.create(tenant=tenant, name='Bomba', slug='bomba')
        variant = ProductVariantModel.objects.create(product=product, sku='BOM-001')
        quote = QuoteModel.objects.create(tenant=tenant, cart=cart, customer_email='cliente@example.com')
        item = QuoteItemModel.objects.create(
            quote=quote,
            product=product,
            variant=variant,
            product_name_snapshot=product.name,
            sku_snapshot=variant.sku,
            attributes_snapshot=variant.attributes_json,
            quantity=3
        )

        self.assertEqual(quote.tenant, tenant)
        self.assertEqual(item.quote, quote)
        self.assertEqual(item.product, product)
        self.assertEqual(item.variant, variant)

    def test_string_representations_are_admin_friendly(self) -> None:
        """ Verify quote models expose admin-friendly labels. """
        tenant = self._create_tenant("quotation-strings")
        quote = QuoteModel.objects.create(tenant=tenant, customer_email='cliente@example.com')
        item = QuoteItemModel.objects.create(quote=quote, product_name_snapshot='Bomba', quantity=1)

        self.assertEqual(str(quote), f'Quote {quote.pk}')
        self.assertEqual(str(item), 'Bomba')

    def test_quote_rejects_source_cart_from_another_tenant(self) -> None:
        """ Verify a quote cannot reference a cart that belongs to another tenant. """
        tenant = self._create_tenant("quotation-cart-scope")
        other_tenant = self._create_tenant("quotation-cart-scope-other")
        foreign_cart = CartModel.objects.create(tenant=other_tenant, session_key="foreign-cart")

        with self.assertRaises(ValidationError):
            QuoteModel.objects.create(
                tenant=tenant,
                cart=foreign_cart,
                customer_email="cliente@example.com",
            )

    def test_model_field_metadata_uses_friendly_translatable_copy(self) -> None:
        """ Verify quotation model fields expose user-friendly labels and help texts. """
        quote_field_expectations = {
            "tenant": ("Business", "Business that owns this quote and the follow-up around it."),
            "user": ("Customer account", "Optional customer account related to this quote."),
            "status": ("Quote status", "Current stage of this quote in your sales follow-up."),
            "notes": ("Internal notes", "Private context for your team. Customers do not need to see this text."),
        }
        item_field_expectations = {
            "quote": ("Quote", "Quote this line item belongs to."),
            "product_name_snapshot": ("Product name snapshot", "Product name captured when this quote item was created."),
            "unit_price_snapshot": ("Unit price snapshot", "Unit price captured when this quote item was created."),
        }

        with override("en"):
            app_config = apps.get_app_config("quotation")

            self.assertEqual("Quotations", str(app_config.verbose_name))

            for field_name, expected_values in quote_field_expectations.items():
                field = QuoteModel._meta.get_field(field_name)
                self.assertEqual(expected_values[0], str(field.verbose_name))
                self.assertEqual(expected_values[1], str(field.help_text))

            for field_name, expected_values in item_field_expectations.items():
                field = QuoteItemModel._meta.get_field(field_name)
                self.assertEqual(expected_values[0], str(field.verbose_name))
                self.assertEqual(expected_values[1], str(field.help_text))
