""" Workflow transition service for owner-managed quotes. """

from collections.abc import Iterable
from dataclasses import dataclass
from django.core.exceptions import ValidationError
from quotation.choices import QuoteWorkflowStatus
from quotation.models import QuoteModel


@dataclass(frozen=True)
class QuoteWorkflowTransitionBatchResult:
    """ Summary for a batch of quote workflow transitions. """

    changed_count: int
    skipped_count: int
    failed_count: int

    @property
    def total_count(self) -> int:
        """ Return the total number of processed quotes.

        Returns:
            int: Changed, skipped, and failed quote count.
        """
        return self.changed_count + self.skipped_count + self.failed_count


class QuoteWorkflowTransitionService:
    """ Transition quotes through the internal owner-managed workflow. """

    @classmethod
    def complete(cls, quote: QuoteModel) -> QuoteModel:
        """ Mark one quote as completed.

        Args:
            quote: Quote to transition.

        Returns:
            QuoteModel: Updated quote.
        """
        return cls.transition(quote, QuoteWorkflowStatus.COMPLETED)

    @classmethod
    def cancel(cls, quote: QuoteModel) -> QuoteModel:
        """ Mark one quote as cancelled.

        Args:
            quote: Quote to transition.

        Returns:
            QuoteModel: Updated quote.
        """
        return cls.transition(quote, QuoteWorkflowStatus.CANCELLED)

    @classmethod
    def transition(cls, quote: QuoteModel, workflow_status: QuoteWorkflowStatus) -> QuoteModel:
        """ Move one quote to a target workflow status.

        Args:
            quote: Quote to transition.
            workflow_status: Target workflow status.

        Returns:
            QuoteModel: Updated quote.

        Raises:
            ValidationError: When the model rejects the workflow transition.
        """
        previous_status = quote.workflow_status
        if previous_status == workflow_status:
            return quote

        quote.workflow_status = workflow_status
        try:
            quote.save()
        except ValidationError:
            quote.workflow_status = previous_status
            raise

        cls.after_transition(
            quote=quote,
            previous_status=previous_status,
            workflow_status=workflow_status,
        )
        return quote

    @classmethod
    def complete_many(cls, quotes: Iterable[QuoteModel]) -> QuoteWorkflowTransitionBatchResult:
        """ Mark a group of quotes as completed.

        Args:
            quotes: Quotes to transition.

        Returns:
            QuoteWorkflowTransitionBatchResult: Batch transition summary.
        """
        return cls.transition_many(quotes, QuoteWorkflowStatus.COMPLETED)

    @classmethod
    def cancel_many(cls, quotes: Iterable[QuoteModel]) -> QuoteWorkflowTransitionBatchResult:
        """ Mark a group of quotes as cancelled.

        Args:
            quotes: Quotes to transition.

        Returns:
            QuoteWorkflowTransitionBatchResult: Batch transition summary.
        """
        return cls.transition_many(quotes, QuoteWorkflowStatus.CANCELLED)

    @classmethod
    def transition_many(
        cls,
        quotes: Iterable[QuoteModel],
        workflow_status: QuoteWorkflowStatus,
    ) -> QuoteWorkflowTransitionBatchResult:
        """ Move a group of quotes to one workflow status.

        Args:
            quotes: Quotes to transition.
            workflow_status: Target workflow status.

        Returns:
            QuoteWorkflowTransitionBatchResult: Batch transition summary.
        """
        changed_count = 0
        skipped_count = 0
        failed_count = 0

        for quote in quotes:
            if quote.workflow_status == workflow_status:
                skipped_count += 1
                continue

            try:
                cls.transition(quote, workflow_status)
                changed_count += 1
            except ValidationError:
                failed_count += 1

        return QuoteWorkflowTransitionBatchResult(
            changed_count=changed_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
        )

    @classmethod
    def after_transition(
        cls,
        *,
        quote: QuoteModel,
        previous_status: str,
        workflow_status: QuoteWorkflowStatus,
    ) -> None:
        """ Run extension hooks after a successful workflow transition.

        Args:
            quote: Quote that changed workflow status.
            previous_status: Workflow status before the transition.
            workflow_status: Workflow status after the transition.
        """
        return None
