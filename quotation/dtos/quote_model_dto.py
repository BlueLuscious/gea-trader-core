from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class QuoteModelDTO:
    """ Public DTO for quote data. """

    id: int
    tenant_id: str
    cart_id: int | None
    user_id: int | None
    workflow_status: str
    customer_name: str
    customer_email: str
    customer_phone: str
    company_name: str
    tax_id: str
    notes: str
    requested_at: datetime | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime
