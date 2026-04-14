""" Master admin registrations for the quotation app. """

from quotation.admin.master.quote_item_model_admin import QuoteItemModelAdmin
from quotation.admin.master.quote_model_admin import QuoteModelAdmin

__all__: list[str] = ["QuoteModelAdmin", "QuoteItemModelAdmin"]
