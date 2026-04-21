from dataclasses import FrozenInstanceError
from decimal import Decimal
from django.utils import timezone
from core.testing.base import LoggedSimpleTestCase
from catalog.dtos import ProductImageModelDTO, ProductModelDTO, ProductVariantModelDTO


class TestCatalogDTO(LoggedSimpleTestCase):
    """ Cover catalog DTO objects. """

    def test_product_model_dto_is_frozen(self) -> None:
        """ Verify ProductModelDTO behaves as an immutable dataclass. """
        dto = ProductModelDTO(
            id=1,
            brand_id=None,
            category_id=None,
            brand_name="",
            category_name="",
            name="Bomba",
            slug="bomba",
            short_description="",
            description="",
            sku_base="BOM",
            is_active=True,
            is_featured=False,
            requires_quote=True,
            active_variant_count=0,
            has_multiple_active_variants=False,
            default_variant_name="",
            image_url="",
            image_alt="Bomba",
            public_price=None,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        with self.assertRaises(FrozenInstanceError):
            dto.name = "Other"

    def test_variant_and_image_dto_store_expected_values(self) -> None:
        """ Verify variant and image DTOs keep structured values intact. """
        now = timezone.now()
        variant_dto = ProductVariantModelDTO(
            id=2,
            product_id=1,
            name="Linea A",
            display_name="Linea A",
            sku="SKU-1",
            attributes_json={"capacidad": "20L"},
            attributes_display=["Capacidad: 20L"],
            price=Decimal('10.50'),
            price_value="10.50",
            price_text="ARS 10.50",
            is_default=True,
            is_active=True,
            sort_order=1,
            image_url="/media/variant.jpg",
            image_alt="Linea A",
            created_at=now,
            updated_at=now,
        )
        image_dto = ProductImageModelDTO(
            id=3,
            product_id=1,
            variant_id=2,
            image_name='catalog/products/images/test.jpg',
            alt_text='Vista frontal',
            sort_order=1,
            is_primary=True,
            created_at=now,
        )

        self.assertEqual(variant_dto.attributes_json['capacidad'], '20L')
        self.assertEqual(image_dto.alt_text, 'Vista frontal')
