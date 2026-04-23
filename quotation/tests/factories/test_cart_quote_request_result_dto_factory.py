""" Tests for the cart quote-request result DTO factory. """

from core.testing.base import LoggedTestCase
from quotation.dtos.factories import CartQuoteRequestResultDTOFactory
from quotation.models import QuoteModel
from tenancy.models import TenantModel


class TestCartQuoteRequestResultDTOFactory(LoggedTestCase):
    """ Cover the cart quote-request result DTO factory. """

    def test_build_maps_quote_and_notification_task_id(self) -> None:
        """ Verify CartQuoteRequestResultDTOFactory.build maps the quote and async task id. """
        tenant = TenantModel.objects.create(name="GEA Trader", slug="gea-trader")
        quote = QuoteModel.objects.create(
            tenant=tenant,
            workflow_status="requested",
            customer_name="Ada Lovelace",
            customer_email="ada@example.com",
            customer_phone="+54 11 5555 0000",
            company_name="Analytical Engines",
        )

        dto = CartQuoteRequestResultDTOFactory.build(
            quote=quote,
            notification_task_id="task-789",
        )

        self.assertEqual(dto.quote.id, quote.id)
        self.assertEqual(dto.quote.workflow_status, quote.workflow_status)
        self.assertEqual(dto.notification_task_id, "task-789")
