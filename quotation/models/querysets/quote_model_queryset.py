from typing import TYPE_CHECKING
from django.db import models
from quotation.choices import QuoteStatus

if TYPE_CHECKING:
    from quotation.models.quote_model import QuoteModel


class QuoteModelQuerySet(models.QuerySet["QuoteModel"]):
    """ QuerySet for reusable quote filters. """

    def drafts(self) -> "QuoteModelQuerySet":
        """ Return draft quotes.

        Returns:
            QuoteModelQuerySet: Draft quotes queryset.
        """
        return self.filter(status=QuoteStatus.DRAFT)

    def requested(self) -> "QuoteModelQuerySet":
        """ Return requested quotes.

        Returns:
            QuoteModelQuerySet: Requested quotes queryset.
        """
        return self.filter(status=QuoteStatus.REQUESTED)

    def active(self) -> "QuoteModelQuerySet":
        """ Return quotes that are still in active business flow.

        Returns:
            QuoteModelQuerySet: Active quotes queryset.
        """
        return self.exclude(status__in=[QuoteStatus.REJECTED, QuoteStatus.EXPIRED])
