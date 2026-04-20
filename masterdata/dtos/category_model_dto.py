""" DTO used to expose category data outside the ORM layer. """

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
    banner_name: str
    parent_id: int | None
    sort_order: int
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime
