""" Owner admin registrations for the quotation app. """

from quotation.admin.owner.quote_item_model_inline import QuoteItemModelInline
from quotation.admin.owner.quote_model_admin import QuoteModelAdmin

__all__: list[str] = ["QuoteModelAdmin", "QuoteItemModelInline"]
