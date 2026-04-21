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
    display_name: str
    sku: str
    attributes_json: dict
    attributes_display: list[str]
    price: Decimal | None
    price_value: str
    price_text: str
    is_default: bool
    is_active: bool
    sort_order: int
    image_url: str
    image_alt: str
    created_at: datetime
    updated_at: datetime
