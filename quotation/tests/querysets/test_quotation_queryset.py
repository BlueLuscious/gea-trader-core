from core.testing.base import LoggedTestCase
from catalog.models import ProductModel, ProductVariantModel
from quotation.choices import QuoteStatus
from quotation.models import QuoteItemModel, QuoteModel


class TestQuotationQuerySet(LoggedTestCase):
    """ Cover quotation queryset helpers. """

    def test_quote_queryset_filters_active_business_flow(self) -> None:
        """ Verify QuoteModelQuerySet.active excludes rejected and expired rows. """
        draft = QuoteModel.objects.create(customer_email='draft@example.com', status=QuoteStatus.DRAFT)
        requested = QuoteModel.objects.create(customer_email='requested@example.com', status=QuoteStatus.REQUESTED)
        QuoteModel.objects.create(customer_email='rejected@example.com', status=QuoteStatus.REJECTED)

        queryset = QuoteModel.objects.get_queryset().active()

        self.assertEqual(set(queryset), {draft, requested})

    def test_quote_item_queryset_filters_by_quote_and_selects_catalog(self) -> None:
        """ Verify QuoteItemModelQuerySet filters by quote and eager loads catalog relations. """
        quote = QuoteModel.objects.create(customer_email='cliente@example.com')
        product = ProductModel.objects.create(name='Filtro', slug='filtro')
        variant = ProductVariantModel.objects.create(product=product, sku='FIL-001')
        item = QuoteItemModel.objects.create(quote=quote, product=product, variant=variant, product_name_snapshot='Filtro', quantity=1)

        queryset = QuoteItemModel.objects.get_queryset().with_catalog().for_quote(quote)

        self.assertQuerySetEqual(queryset, [item], transform=lambda instance: instance)
        self.assertIn('product', queryset.query.select_related)
        self.assertIn('variant', queryset.query.select_related)
