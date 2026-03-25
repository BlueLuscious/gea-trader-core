from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from quotation.models.quote_model import QuoteModel


class QuoteModelQuerySet(models.QuerySet["QuoteModel"]):
    """ QuerySet for reusable quote filters. """

    def drafts(self) -> "QuoteModelQuerySet":
        """ Return draft quotes.

        Returns:
            QuoteModelQuerySet: Draft quotes queryset.
        """
        return self.filter(status="draft")

    def requested(self) -> "QuoteModelQuerySet":
        """ Return requested quotes.

        Returns:
            QuoteModelQuerySet: Requested quotes queryset.
        """
        return self.filter(status="requested")

    def active(self) -> "QuoteModelQuerySet":
        """ Return quotes that are still in active business flow.

        Returns:
            QuoteModelQuerySet: Active quotes queryset.
        """
        return self.exclude(status__in=["rejected", "expired"])
