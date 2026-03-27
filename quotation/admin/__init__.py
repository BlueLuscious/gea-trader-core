""" Quotation admin package. """

from quotation.admin.master import QuoteItemModelAdmin, QuoteModelAdmin

__all__: list[str] = ["QuoteModelAdmin", "QuoteItemModelAdmin"]
