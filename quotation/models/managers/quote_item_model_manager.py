from typing import TYPE_CHECKING
from django.db import models
from quotation.models.querysets.quote_item_model_queryset import QuoteItemModelQuerySet

if TYPE_CHECKING:
    from quotation.models import QuoteItemModel, QuoteModel


class QuoteItemModelManager(models.Manager["QuoteItemModel"]):
    """ Manager exposing typed quote item queryset helpers. """

    def get_queryset(self) -> "QuoteItemModelQuerySet":
        """ Return the base queryset for quote item queries.

        Returns:
            QuoteItemModelQuerySet: Specialized queryset for quote items.
        """
        return QuoteItemModelQuerySet(self.model, using=self._db)

    def with_catalog(self) -> "QuoteItemModelQuerySet":
        """ Return quote items with catalog relations eager loaded.

        Returns:
            QuoteItemModelQuerySet: Queryset with product and variant loaded.
        """
        return self.get_queryset().with_catalog()

    def for_quote(self, quote: "QuoteModel") -> "QuoteItemModelQuerySet":
        """ Return items for a quote.

        Args:
            quote: Quote instance or compatible lookup value.

        Returns:
            QuoteItemModelQuerySet: Quote items queryset.
        """
        return self.get_queryset().for_quote(quote)
