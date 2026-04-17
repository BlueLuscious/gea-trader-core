from typing import TYPE_CHECKING
from django.db import models
from quotation.choices import QuoteWorkflowStatus

if TYPE_CHECKING:
    from quotation.models.quote_model import QuoteModel
    from tenancy.models import TenantModel


class QuoteModelQuerySet(models.QuerySet["QuoteModel"]):
    """ QuerySet for reusable quote filters. """

    def for_tenant(self, tenant: "TenantModel") -> "QuoteModelQuerySet":
        """ Return quotes owned by one tenant.

        Args:
            tenant: Tenant that owns the quotes.

        Returns:
            QuoteModelQuerySet: Tenant-scoped quotes queryset.
        """
        return self.filter(tenant=tenant)

    def drafts(self) -> "QuoteModelQuerySet":
        """ Return draft quotes.

        Returns:
            QuoteModelQuerySet: Draft quotes queryset.
        """
        return self.filter(workflow_status=QuoteWorkflowStatus.DRAFT)

    def requested(self) -> "QuoteModelQuerySet":
        """ Return requested quotes.

        Returns:
            QuoteModelQuerySet: Requested quotes queryset.
        """
        return self.filter(workflow_status=QuoteWorkflowStatus.REQUESTED)

    def in_progress(self) -> "QuoteModelQuerySet":
        """ Return in-progress quotes.

        Returns:
            QuoteModelQuerySet: In-progress quotes queryset.
        """
        return self.filter(workflow_status=QuoteWorkflowStatus.IN_PROGRESS)

    def active(self) -> "QuoteModelQuerySet":
        """ Return quotes that are still in active business flow.

        Returns:
            QuoteModelQuerySet: Active quotes queryset.
        """
        return self.exclude(
            workflow_status__in=(QuoteWorkflowStatus.COMPLETED, QuoteWorkflowStatus.CANCELLED)
        )
