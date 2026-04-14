from core.testing.base import LoggedTestCase
from catalog.models import ProductModel, ProductVariantModel
from tenancy.models import TenantModel
from quotation.choices import QuoteStatus
from quotation.models import QuoteItemModel, QuoteModel


class TestQuotationQuerySet(LoggedTestCase):
    """ Cover quotation queryset helpers. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for catalog-linked quotation fixtures.

        Args:
            slug: Stable tenant slug.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_quote_queryset_filters_active_business_flow(self) -> None:
        """ Verify QuoteModelQuerySet.active excludes rejected and expired rows. """
        tenant = self._create_tenant("quotation-active")
        draft = QuoteModel.objects.create(tenant=tenant, customer_email='draft@example.com', status=QuoteStatus.DRAFT)
        requested = QuoteModel.objects.create(tenant=tenant, customer_email='requested@example.com', status=QuoteStatus.REQUESTED)
        QuoteModel.objects.create(tenant=tenant, customer_email='rejected@example.com', status=QuoteStatus.REJECTED)

        queryset = QuoteModel.objects.get_queryset().active()

        self.assertEqual(set(queryset), {draft, requested})

    def test_quote_queryset_filters_by_tenant(self) -> None:
        """ Verify QuoteModelQuerySet.for_tenant returns only quotes owned by the chosen tenant. """
        tenant = self._create_tenant("quotation-queryset-north")
        other_tenant = self._create_tenant("quotation-queryset-south")
        first_quote = QuoteModel.objects.create(tenant=tenant, customer_email='north@example.com')
        QuoteModel.objects.create(tenant=other_tenant, customer_email='south@example.com')

        queryset = QuoteModel.objects.get_queryset().for_tenant(tenant)

        self.assertEqual([first_quote], list(queryset))

    def test_quote_item_queryset_filters_by_quote_and_selects_catalog(self) -> None:
        """ Verify QuoteItemModelQuerySet filters by quote and eager loads catalog relations. """
        tenant = self._create_tenant("quotation-queryset")
        quote = QuoteModel.objects.create(tenant=tenant, customer_email='cliente@example.com')
        product = ProductModel.objects.create(tenant=tenant, name='Filtro', slug='filtro')
        variant = ProductVariantModel.objects.create(product=product, sku='FIL-001')
        item = QuoteItemModel.objects.create(quote=quote, product=product, variant=variant, product_name_snapshot='Filtro', quantity=1)

        queryset = QuoteItemModel.objects.get_queryset().with_catalog().for_quote(quote)

        self.assertQuerySetEqual(queryset, [item], transform=lambda instance: instance)
        self.assertIn('product', queryset.query.select_related)
        self.assertIn('variant', queryset.query.select_related)

    def test_quote_item_queryset_filters_by_tenant(self) -> None:
        """ Verify QuoteItemModelQuerySet.for_tenant scopes quote items through the parent quote. """
        tenant = self._create_tenant("quotation-items-north")
        other_tenant = self._create_tenant("quotation-items-south")
        first_quote = QuoteModel.objects.create(tenant=tenant, customer_email='north@example.com')
        second_quote = QuoteModel.objects.create(tenant=other_tenant, customer_email='south@example.com')
        north_item = QuoteItemModel.objects.create(quote=first_quote, product_name_snapshot='Bomba', quantity=1)
        QuoteItemModel.objects.create(quote=second_quote, product_name_snapshot='Filtro', quantity=2)

        queryset = QuoteItemModel.objects.get_queryset().for_tenant(tenant)

        self.assertEqual([north_item], list(queryset))
