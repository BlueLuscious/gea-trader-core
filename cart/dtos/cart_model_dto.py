""" DTO used to expose cart data outside the ORM layer. """

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CartModelDTO:
    """ Public DTO for cart data. """

    id: int
    tenant_id: str
    user_id: int | None
    session_key: str
    status: str
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime
