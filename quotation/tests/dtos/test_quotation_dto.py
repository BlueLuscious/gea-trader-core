from dataclasses import FrozenInstanceError
from decimal import Decimal
from django.utils import timezone
from core.testing.base import LoggedSimpleTestCase
from quotation.dtos import QuoteItemModelDTO, QuoteModelDTO


class TestQuotationDTO(LoggedSimpleTestCase):
    """ Cover quotation DTO objects. """

    def test_quote_model_dto_is_frozen(self) -> None:
        """ Verify QuoteModelDTO behaves as an immutable dataclass. """
        dto = QuoteModelDTO(
            id=1,
            tenant_id="tenant-1",
            cart_id=None,
            user_id=None,
            status='draft',
            customer_name='',
            customer_email='cliente@example.com',
            customer_phone='',
            company_name='',
            tax_id='',
            notes='',
            requested_at=None,
            sent_at=None,
            answered_at=None,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

        with self.assertRaises(FrozenInstanceError):
            dto.status = 'requested'

    def test_quote_item_model_dto_keeps_snapshot_values(self) -> None:
        """ Verify QuoteItemModelDTO preserves snapshot and pricing values. """
        dto = QuoteItemModelDTO(
            id=2,
            quote_id=1,
            product_id=3,
            variant_id=4,
            product_name_snapshot='Bomba',
            sku_snapshot='BOM-001',
            attributes_snapshot={'viscosidad': '46'},
            unit_price_snapshot=Decimal('25.00'),
            quantity=2,
            notes='Urgente',
            created_at=timezone.now()
        )

        self.assertEqual(dto.attributes_snapshot['viscosidad'], '46')
        self.assertEqual(dto.unit_price_snapshot, Decimal('25.00'))
