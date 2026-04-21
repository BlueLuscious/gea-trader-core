""" DTO used to expose catalog product data outside the ORM layer. """

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class ProductModelDTO:
    """ Public DTO for product data. """

    id: int
    brand_id: int | None
    category_id: int | None
    brand_name: str
    category_name: str
    name: str
    slug: str
    short_description: str
    description: str
    sku_base: str
    is_active: bool
    is_featured: bool
    requires_quote: bool
    active_variant_count: int
    has_multiple_active_variants: bool
    default_variant_name: str
    image_url: str
    image_alt: str
    public_price: Decimal | None
    created_at: datetime
    updated_at: datetime
