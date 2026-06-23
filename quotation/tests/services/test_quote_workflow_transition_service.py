""" Tests for quote workflow transition services. """

from unittest.mock import patch
from django.core.exceptions import ValidationError
from core.testing.base import LoggedTestCase
from quotation.choices import QuoteWorkflowStatus
from quotation.models import QuoteModel
from quotation.services import QuoteWorkflowTransitionService
from tenancy.models import TenantModel


class TestQuoteWorkflowTransitionService(LoggedTestCase):
    """ Verify quote workflow transitions stay centralized in the service layer. """

    def setUp(self) -> None:
        """ Create a tenant used by quote workflow transition tests. """
        self.tenant = TenantModel.objects.create(name="Quotation Workflow", slug="quotation-workflow")

    def test_complete_marks_quote_as_completed_and_sets_resolution_timestamp(self) -> None:
        """ Verify completing one quote updates workflow status and terminal timestamp. """
        quote = QuoteModel.objects.create(tenant=self.tenant, customer_email="customer@example.com")

        with patch.object(QuoteWorkflowTransitionService, "after_transition") as after_transition_mock:
            updated_quote = QuoteWorkflowTransitionService.complete(quote)

        updated_quote.refresh_from_db()

        self.assertEqual(QuoteWorkflowStatus.COMPLETED, updated_quote.workflow_status)
        self.assertIsNotNone(updated_quote.requested_at)
        self.assertIsNotNone(updated_quote.resolved_at)
        after_transition_mock.assert_called_once_with(
            quote=updated_quote,
            previous_status=QuoteWorkflowStatus.DRAFT,
            workflow_status=QuoteWorkflowStatus.COMPLETED,
        )

    def test_cancel_marks_quote_as_cancelled_and_sets_resolution_timestamp(self) -> None:
        """ Verify cancelling one quote updates workflow status and terminal timestamp. """
        quote = QuoteModel.objects.create(tenant=self.tenant, customer_email="customer@example.com")

        updated_quote = QuoteWorkflowTransitionService.cancel(quote)
        updated_quote.refresh_from_db()

        self.assertEqual(QuoteWorkflowStatus.CANCELLED, updated_quote.workflow_status)
        self.assertIsNotNone(updated_quote.requested_at)
        self.assertIsNotNone(updated_quote.resolved_at)

    def test_transition_rejects_terminal_status_switches(self) -> None:
        """ Verify the service preserves model-level terminal workflow rules. """
        quote = QuoteModel.objects.create(
            tenant=self.tenant,
            customer_email="customer@example.com",
            workflow_status=QuoteWorkflowStatus.COMPLETED,
        )

        with self.assertRaises(ValidationError):
            QuoteWorkflowTransitionService.cancel(quote)

        self.assertEqual(QuoteWorkflowStatus.COMPLETED, quote.workflow_status)

    def test_transition_many_reports_changed_skipped_and_failed_counts(self) -> None:
        """ Verify bulk transitions summarize changed, skipped, and failed quotes. """
        open_quote = QuoteModel.objects.create(tenant=self.tenant, customer_email="open@example.com")
        completed_quote = QuoteModel.objects.create(
            tenant=self.tenant,
            customer_email="completed@example.com",
            workflow_status=QuoteWorkflowStatus.COMPLETED,
        )
        cancelled_quote = QuoteModel.objects.create(
            tenant=self.tenant,
            customer_email="cancelled@example.com",
            workflow_status=QuoteWorkflowStatus.CANCELLED,
        )

        result = QuoteWorkflowTransitionService.complete_many((open_quote, completed_quote, cancelled_quote))
        open_quote.refresh_from_db()

        self.assertEqual(1, result.changed_count)
        self.assertEqual(1, result.skipped_count)
        self.assertEqual(1, result.failed_count)
        self.assertEqual(3, result.total_count)
        self.assertEqual(QuoteWorkflowStatus.COMPLETED, open_quote.workflow_status)
