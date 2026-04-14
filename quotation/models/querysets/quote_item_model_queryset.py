from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from quotation.models import QuoteItemModel, QuoteModel
    from tenancy.models import TenantModel


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

    def for_tenant(self, tenant: "TenantModel") -> "QuoteItemModelQuerySet":
        """ Return quote items that belong to one tenant through their parent quote.

        Args:
            tenant: Tenant that owns the parent quotes.

        Returns:
            QuoteItemModelQuerySet: Tenant-scoped quote items queryset.
        """
        return self.filter(quote__tenant=tenant)
