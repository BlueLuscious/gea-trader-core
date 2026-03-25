from dataclasses import FrozenInstanceError
from datetime import datetime
from django.utils import timezone
from core.testing.base import LoggedSimpleTestCase
from masterdata.dtos import BrandModelDTO, CategoryModelDTO


class TestMasterdataDTO(LoggedSimpleTestCase):
    """ Cover masterdata DTO objects. """

    def test_brand_model_dto_is_frozen(self) -> None:
        """ Verify BrandModelDTO behaves as an immutable dataclass. """
        dto = BrandModelDTO(
            id=1,
            name="GEA",
            slug="gea",
            description="",
            is_active=True,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        with self.assertRaises(FrozenInstanceError):
            dto.name = "Other"

    def test_category_model_dto_keeps_parent_id(self) -> None:
        """ Verify CategoryModelDTO stores the parent identifier as expected. """
        now: datetime = timezone.now()
        dto = CategoryModelDTO(
            id=2,
            name="Lubricacion",
            slug="lubricacion",
            description="",
            parent_id=1,
            sort_order=10,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        self.assertEqual(dto.parent_id, 1)
        self.assertEqual(dto.sort_order, 10)
