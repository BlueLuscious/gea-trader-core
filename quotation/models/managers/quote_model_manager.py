from typing import TYPE_CHECKING
from django.db import models
from quotation.models.querysets.quote_model_queryset import QuoteModelQuerySet

if TYPE_CHECKING:
    from quotation.models.quote_model import QuoteModel


class QuoteModelManager(models.Manager["QuoteModel"]):
    """ Manager exposing typed quote queryset helpers. """

    def get_queryset(self) -> "QuoteModelQuerySet":
        """ Return the base queryset for quote queries.

        Returns:
            QuoteModelQuerySet: Specialized queryset for quotes.
        """
        return QuoteModelQuerySet(self.model, using=self._db)

    def drafts(self) -> "QuoteModelQuerySet":
        """ Return draft quotes.

        Returns:
            QuoteModelQuerySet: Draft quotes queryset.
        """
        return self.get_queryset().drafts()

    def requested(self) -> "QuoteModelQuerySet":
        """ Return requested quotes.

        Returns:
            QuoteModelQuerySet: Requested quotes queryset.
        """
        return self.get_queryset().requested()

    def active(self) -> "QuoteModelQuerySet":
        """ Return active quotes.

        Returns:
            QuoteModelQuerySet: Active quotes queryset.
        """
        return self.get_queryset().active()
