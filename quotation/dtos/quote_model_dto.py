from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class QuoteModelDTO:
    """ Public DTO for quote data. """

    id: int
    cart_id: int | None
    user_id: int | None
    status: str
    customer_name: str
    customer_email: str
    customer_phone: str
    company_name: str
    tax_id: str
    notes: str
    requested_at: datetime | None
    sent_at: datetime | None
    answered_at: datetime | None
    created_at: datetime
    updated_at: datetime
