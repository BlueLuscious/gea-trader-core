""" DTO used to expose catalog variant data outside the ORM layer. """

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class ProductVariantModelDTO:
    """ Public DTO for product variant data. """

    id: int
    product_id: int
    name: str
    sku: str
    attributes_json: dict
    price: Decimal | None
    is_default: bool
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
