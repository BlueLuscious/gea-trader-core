from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CategoryModelDTO:
    """ Public DTO for category data. """

    id: int
    tenant_id: str
    name: str
    slug: str
    description: str
    parent_id: int | None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
