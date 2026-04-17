from core.testing.base import LoggedTestCase
from catalog.models import ProductModel, ProductVariantModel
from tenancy.models import TenantModel
from quotation.choices import QuoteWorkflowStatus
from quotation.models import QuoteItemModel, QuoteModel


class TestQuotationManager(LoggedTestCase):
    """ Cover quotation manager helpers. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for catalog-linked quotation fixtures.

        Args:
            slug: Stable tenant slug.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_quote_manager_filters_workflow_statuses(self) -> None:
        """ Verify quote manager helpers expose internal workflow subsets. """
        tenant = self._create_tenant("quotation-manager-status")
        draft = QuoteModel.objects.create(
            tenant=tenant,
            customer_email='draft@example.com',
            workflow_status=QuoteWorkflowStatus.DRAFT,
        )
        requested = QuoteModel.objects.create(
            tenant=tenant,
            customer_email='requested@example.com',
            workflow_status=QuoteWorkflowStatus.REQUESTED,
        )
        in_progress = QuoteModel.objects.create(
            tenant=tenant,
            customer_email='progress@example.com',
            workflow_status=QuoteWorkflowStatus.IN_PROGRESS,
        )
        QuoteModel.objects.create(
            tenant=tenant,
            customer_email='completed@example.com',
            workflow_status=QuoteWorkflowStatus.COMPLETED,
        )
        QuoteModel.objects.create(
            tenant=tenant,
            customer_email='cancelled@example.com',
            workflow_status=QuoteWorkflowStatus.CANCELLED,
        )

        self.assertQuerySetEqual(QuoteModel.objects.drafts(), [draft], transform=lambda instance: instance)
        self.assertQuerySetEqual(QuoteModel.objects.requested(), [requested], transform=lambda instance: instance)
        self.assertQuerySetEqual(QuoteModel.objects.in_progress(), [in_progress], transform=lambda instance: instance)
        self.assertEqual(set(QuoteModel.objects.active()), {draft, requested, in_progress})

    def test_quote_manager_filters_by_tenant(self) -> None:
        """ Verify quote manager exposes tenant-scoped access to quote roots. """
        tenant = self._create_tenant("quotation-manager-north")
        other_tenant = self._create_tenant("quotation-manager-south")
        first_quote = QuoteModel.objects.create(tenant=tenant, customer_email='north@example.com')
        QuoteModel.objects.create(tenant=other_tenant, customer_email='south@example.com')

        self.assertQuerySetEqual(QuoteModel.objects.for_tenant(tenant), [first_quote], transform=lambda instance: instance)

    def test_quote_item_manager_filters_and_selects_catalog(self) -> None:
        """ Verify quote item manager helpers filter by quote and eager load catalog relations. """
        tenant = self._create_tenant("quotation-manager")
        other_tenant = self._create_tenant("quotation-manager-other")
        quote = QuoteModel.objects.create(tenant=tenant, customer_email='cliente@example.com')
        other_quote = QuoteModel.objects.create(tenant=other_tenant, customer_email='otro@example.com')
        product = ProductModel.objects.create(tenant=tenant, name='Bomba', slug='bomba')
        variant = ProductVariantModel.objects.create(product=product, sku='BOM-001')
        matching_item = QuoteItemModel.objects.create(quote=quote, product=product, variant=variant, product_name_snapshot='Bomba', quantity=1)
        QuoteItemModel.objects.create(quote=other_quote, product=product, variant=variant, product_name_snapshot='Bomba', quantity=2)

        self.assertQuerySetEqual(QuoteItemModel.objects.for_quote(quote), [matching_item], transform=lambda instance: instance)
        self.assertIn('product', QuoteItemModel.objects.with_catalog().query.select_related)
        self.assertIn('variant', QuoteItemModel.objects.with_catalog().query.select_related)

    def test_quote_item_manager_filters_by_tenant(self) -> None:
        """ Verify quote item manager exposes tenant-scoped access through the parent quote. """
        tenant = self._create_tenant("quotation-item-manager-north")
        other_tenant = self._create_tenant("quotation-item-manager-south")
        quote = QuoteModel.objects.create(tenant=tenant, customer_email='north@example.com')
        other_quote = QuoteModel.objects.create(tenant=other_tenant, customer_email='south@example.com')
        matching_item = QuoteItemModel.objects.create(quote=quote, product_name_snapshot='Bomba', quantity=1)
        QuoteItemModel.objects.create(quote=other_quote, product_name_snapshot='Filtro', quantity=2)

        self.assertQuerySetEqual(QuoteItemModel.objects.for_tenant(tenant), [matching_item], transform=lambda instance: instance)
