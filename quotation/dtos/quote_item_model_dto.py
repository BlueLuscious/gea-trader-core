from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class QuoteItemModelDTO:
    """ Public DTO for quote item snapshot data. """

    id: int
    quote_id: int
    product_id: int | None
    variant_id: int | None
    product_name_snapshot: str
    sku_snapshot: str
    attributes_snapshot: dict
    unit_price_snapshot: Decimal | None
    quantity: int
    notes: str
    created_at: datetime
