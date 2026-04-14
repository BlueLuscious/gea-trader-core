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
        cart = CartModel.objects.create(session_key='session-quote')
        tenant = self._create_tenant("quotation-model")
        product = ProductModel.objects.create(tenant=tenant, name='Bomba', slug='bomba')
        variant = ProductVariantModel.objects.create(product=product, sku='BOM-001')
        quote = QuoteModel.objects.create(cart=cart, customer_email='cliente@example.com')
        item = QuoteItemModel.objects.create(
            quote=quote,
            product=product,
            variant=variant,
            product_name_snapshot=product.name,
            sku_snapshot=variant.sku,
            attributes_snapshot=variant.attributes_json,
            quantity=3
        )

        self.assertEqual(item.quote, quote)
        self.assertEqual(item.product, product)
        self.assertEqual(item.variant, variant)

    def test_string_representations_are_admin_friendly(self) -> None:
        """ Verify quote models expose admin-friendly labels. """
        quote = QuoteModel.objects.create(customer_email='cliente@example.com')
        item = QuoteItemModel.objects.create(quote=quote, product_name_snapshot='Bomba', quantity=1)

        self.assertEqual(str(quote), f'Quote {quote.pk}')
        self.assertEqual(str(item), 'Bomba')
