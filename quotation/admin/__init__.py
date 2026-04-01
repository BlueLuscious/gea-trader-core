""" Quotation admin package. """

from quotation.admin.master import QuoteItemModelAdmin, QuoteModelAdmin
from quotation.admin.owner import QuoteItemModelInline
from quotation.admin.owner import QuoteModelAdmin as OwnerQuoteModelAdmin

__all__: list[str] = [
    "QuoteModelAdmin",
    "QuoteItemModelAdmin",
    "OwnerQuoteModelAdmin",
    "QuoteItemModelInline",
]
