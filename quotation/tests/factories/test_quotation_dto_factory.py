from core.testing.base import LoggedTestCase
from quotation.dtos.factories import QuoteItemModelDTOFactory, QuoteModelDTOFactory
from quotation.models import QuoteItemModel, QuoteModel
from tenancy.models import TenantModel


class TestQuotationDTOFactory(LoggedTestCase):
    """ Cover quotation DTO factories. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for quotation DTO factory tests.

        Args:
            slug: Stable tenant slug.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_quote_model_dto_factory_build_maps_fields(self) -> None:
        """ Verify QuoteModelDTOFactory.build maps quote fields. """
        tenant = self._create_tenant("quotation-dto-factory")
        quote = QuoteModel.objects.create(tenant=tenant, customer_email='cliente@example.com', company_name='GEA')

        dto = QuoteModelDTOFactory.build(quote)

        self.assertEqual(dto.id, quote.id)
        self.assertEqual(dto.tenant_id, str(tenant.pk))
        self.assertEqual(dto.customer_email, 'cliente@example.com')
        self.assertEqual(dto.company_name, 'GEA')

    def test_quote_item_model_dto_factory_copies_attributes_snapshot(self) -> None:
        """ Verify QuoteItemModelDTOFactory copies the snapshot dictionary. """
        tenant = self._create_tenant("quotation-item-dto-factory")
        item = QuoteItemModel.objects.create(
            quote=QuoteModel.objects.create(tenant=tenant, customer_email='cliente@example.com'),
            product_name_snapshot='Bomba',
            sku_snapshot='BOM-001',
            attributes_snapshot={'viscosidad': '46'},
            quantity=2
        )

        dto = QuoteItemModelDTOFactory.build(item)
        item.attributes_snapshot['viscosidad'] = '68'

        self.assertEqual(dto.attributes_snapshot['viscosidad'], '46')

    def test_quote_item_model_dto_factory_build_many_returns_all_items(self) -> None:
        """ Verify QuoteItemModelDTOFactory.build_many returns DTOs for each quote item. """
        tenant = self._create_tenant("quotation-build-many")
        quote = QuoteModel.objects.create(tenant=tenant, customer_email='cliente@example.com')
        first = QuoteItemModel.objects.create(quote=quote, product_name_snapshot='Bomba', quantity=1)
        second = QuoteItemModel.objects.create(quote=quote, product_name_snapshot='Filtro', quantity=3)

        dtos = QuoteItemModelDTOFactory.build_many([first, second])

        self.assertEqual([dto.product_name_snapshot for dto in dtos], ['Bomba', 'Filtro'])
        self.assertEqual([dto.quantity for dto in dtos], [1, 3])
