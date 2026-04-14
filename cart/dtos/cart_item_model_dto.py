from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CartItemModelDTO:
    """ Public DTO for cart item data. """

    id: int
    cart_id: int
    product_id: int
    variant_id: int | None
    quantity: int
    notes: str
    created_at: datetime
    updated_at: datetime
