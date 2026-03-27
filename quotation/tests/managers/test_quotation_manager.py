from core.testing.base import LoggedTestCase
from catalog.models import ProductModel, ProductVariantModel
from quotation.choices import QuoteStatus
from quotation.models import QuoteItemModel, QuoteModel


class TestQuotationManager(LoggedTestCase):
    """ Cover quotation manager helpers. """

    def test_quote_manager_filters_statuses(self) -> None:
        """ Verify quote manager helpers expose lifecycle subsets. """
        draft = QuoteModel.objects.create(customer_email='draft@example.com', status=QuoteStatus.DRAFT)
        requested = QuoteModel.objects.create(customer_email='requested@example.com', status=QuoteStatus.REQUESTED)
        active_sent = QuoteModel.objects.create(customer_email='sent@example.com', status=QuoteStatus.SENT)
        QuoteModel.objects.create(customer_email='expired@example.com', status=QuoteStatus.EXPIRED)

        self.assertQuerySetEqual(QuoteModel.objects.drafts(), [draft], transform=lambda instance: instance)
        self.assertQuerySetEqual(QuoteModel.objects.requested(), [requested], transform=lambda instance: instance)
        self.assertEqual(set(QuoteModel.objects.active()), {draft, requested, active_sent})

    def test_quote_item_manager_filters_and_selects_catalog(self) -> None:
        """ Verify quote item manager helpers filter by quote and eager load catalog relations. """
        quote = QuoteModel.objects.create(customer_email='cliente@example.com')
        other_quote = QuoteModel.objects.create(customer_email='otro@example.com')
        product = ProductModel.objects.create(name='Bomba', slug='bomba')
        variant = ProductVariantModel.objects.create(product=product, sku='BOM-001')
        matching_item = QuoteItemModel.objects.create(quote=quote, product=product, variant=variant, product_name_snapshot='Bomba', quantity=1)
        QuoteItemModel.objects.create(quote=other_quote, product=product, variant=variant, product_name_snapshot='Bomba', quantity=2)

        self.assertQuerySetEqual(QuoteItemModel.objects.for_quote(quote), [matching_item], transform=lambda instance: instance)
        self.assertIn('product', QuoteItemModel.objects.with_catalog().query.select_related)
        self.assertIn('variant', QuoteItemModel.objects.with_catalog().query.select_related)
