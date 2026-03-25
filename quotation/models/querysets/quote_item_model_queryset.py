from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from quotation.models import QuoteItemModel, QuoteModel


class QuoteItemModelQuerySet(models.QuerySet["QuoteItemModel"]):
    """ QuerySet for reusable quote item filters. """

    def with_catalog(self) -> "QuoteItemModelQuerySet":
        """ Eager load product and variant relations.

        Returns:
            QuoteItemModelQuerySet: Queryset with catalog relations loaded.
        """
        return self.select_related("product", "variant")

    def for_quote(self, quote: "QuoteModel") -> "QuoteItemModelQuerySet":
        """ Return items for a quote.

        Args:
            quote: Quote instance or compatible lookup value.

        Returns:
            QuoteItemModelQuerySet: Quote items queryset.
        """
        return self.filter(quote=quote)
