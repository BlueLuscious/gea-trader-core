""" Tests for the cart quote-request result DTO. """

from dataclasses import FrozenInstanceError

from core.testing import LoggedSimpleTestCase
from django.utils import timezone
from quotation.dtos import CartQuoteRequestResultDTO, QuoteModelDTO


class TestCartQuoteRequestResultDTO(LoggedSimpleTestCase):
    """ Cover cart quote-request result DTO objects. """

    def test_cart_quote_request_result_dto_is_frozen(self) -> None:
        """ Verify CartQuoteRequestResultDTO behaves as an immutable dataclass. """
        dto = CartQuoteRequestResultDTO(
            quote=QuoteModelDTO(
                id=1,
                tenant_id="tenant-1",
                cart_id=10,
                user_id=None,
                workflow_status="requested",
                customer_name="Ada Lovelace",
                customer_email="ada@example.com",
                customer_phone="+54 11 5555 0000",
                company_name="Analytical Engines",
                tax_id="",
                notes="Necesito una cotización.",
                requested_at=None,
                resolved_at=None,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            ),
            notification_task_id="task-123",
        )

        with self.assertRaises(FrozenInstanceError):
            dto.notification_task_id = "task-456"
