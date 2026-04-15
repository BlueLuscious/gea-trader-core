from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BrandModelDTO:
    """ Public DTO for brand data. """

    id: int
    tenant_id: str
    name: str
    slug: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
