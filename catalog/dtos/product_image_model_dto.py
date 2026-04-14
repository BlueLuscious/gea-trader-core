from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ProductImageModelDTO:
    """ Public DTO for product image data. """

    id: int
    product_id: int
    variant_id: int | None
    image_name: str
    alt_text: str
    sort_order: int
    is_primary: bool
    created_at: datetime
