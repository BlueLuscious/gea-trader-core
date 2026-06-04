from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile
from core.testing.base import LoggedTestCase
from catalog.dtos.factories import ProductImageModelDTOFactory, ProductModelDTOFactory, ProductVariantModelDTOFactory
from catalog.models import ProductImageModel, ProductModel, ProductVariantModel
from tenancy.models import TenantModel


class TestCatalogDTOFactory(LoggedTestCase):
    """ Cover catalog DTO factories. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for DTO factory source models.

        Args:
            slug: Stable slug for the tenant.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_product_model_dto_factory_build_maps_fields(self) -> None:
        """ Verify ProductModelDTOFactory.build maps core product fields and public price. """
        tenant = self._create_tenant("north")
        product = ProductModel.objects.create(
            tenant=tenant,
            name='Bomba',
            slug='bomba',
            sku_base='BOM',
            is_featured=True,
            requires_quote=False,
        )
        ProductVariantModel.objects.create(
            product=product,
            sku='BOM-001',
            price=Decimal('20.00'),
            is_default=True,
        )

        dto = ProductModelDTOFactory.build(product)

        self.assertEqual(dto.id, product.id)
        self.assertEqual(dto.sku_base, 'BOM')
        self.assertTrue(dto.is_featured)
        self.assertEqual(dto.public_price, Decimal('20.00'))
        self.assertEqual(dto.active_variant_count, 1)
        self.assertFalse(dto.has_multiple_active_variants)
        self.assertEqual(dto.brand_name, "")
        self.assertEqual(dto.category_name, "")
        self.assertEqual(dto.default_variant_name, "BOM-001")

    def test_product_model_dto_factory_maps_active_variant_count_fields(self) -> None:
        """ Verify ProductModelDTOFactory exposes active-variant count semantics. """
        tenant = self._create_tenant("variants")
        product = ProductModel.objects.create(
            tenant=tenant,
            name='Valve Pack',
            slug='valve-pack',
            requires_quote=True,
        )
        ProductVariantModel.objects.create(
            product=product,
            sku='VAL-001',
            is_active=True,
        )
        ProductVariantModel.objects.create(
            product=product,
            sku='VAL-002',
            is_active=True,
        )
        ProductVariantModel.objects.create(
            product=product,
            sku='VAL-003',
            is_active=False,
        )

        dto = ProductModelDTOFactory.build(product)

        self.assertEqual(dto.active_variant_count, 2)
        self.assertTrue(dto.has_multiple_active_variants)

    def test_product_model_dto_factory_hides_public_price_for_quote_only_products(self) -> None:
        """ Verify ProductModelDTOFactory keeps quote-only product prices internal. """
        tenant = self._create_tenant("quote-only")
        product = ProductModel.objects.create(
            tenant=tenant,
            name='Filtro',
            slug='filtro',
            requires_quote=True,
        )
        ProductVariantModel.objects.create(
            product=product,
            sku='FIL-001',
            price=Decimal('15.00'),
            is_default=True,
        )

        dto = ProductModelDTOFactory.build(product)

        self.assertIsNone(dto.public_price)

    def test_variant_factory_copies_attributes_json(self) -> None:
        """ Verify ProductVariantModelDTOFactory copies the attributes dictionary. """
        tenant = self._create_tenant("north")
        product = ProductModel.objects.create(tenant=tenant, name='Filtro', slug='filtro')
        variant = ProductVariantModel.objects.create(product=product, sku='FIL-001', attributes_json={'viscosidad': '46'}, price=Decimal('15.00'))

        dto = ProductVariantModelDTOFactory.build(variant)
        variant.attributes_json['viscosidad'] = '68'

        self.assertEqual(dto.attributes_json['viscosidad'], '46')
        self.assertEqual(dto.attributes_display, ['Viscosidad: 46'])
        self.assertEqual(dto.price, Decimal('15.00'))
        self.assertEqual(dto.price_value, '15.00')
        self.assertEqual(dto.price_text, 'ARS 15.00')

    def test_variant_factory_uses_effective_sku(self) -> None:
        """ Verify ProductVariantModelDTOFactory exposes the product SKU fallback. """
        tenant = self._create_tenant("variant-dto-sku-fallback")
        product = ProductModel.objects.create(
            tenant=tenant,
            name="Filtro",
            slug="filtro",
            sku_base="FIL-BASE",
        )
        variant = ProductVariantModel.objects.create(product=product, sku="")

        dto = ProductVariantModelDTOFactory.build(variant)

        self.assertEqual(dto.sku, "FIL-BASE")
        self.assertEqual(dto.display_name, "FIL-BASE")

    def test_image_factory_build_many_returns_expected_names(self) -> None:
        """ Verify ProductImageModelDTOFactory.build_many keeps image metadata. """
        tenant = self._create_tenant("north")
        product = ProductModel.objects.create(tenant=tenant, name='Aceite', slug='aceite')
        first = ProductImageModel.objects.create(product=product, image=SimpleUploadedFile('aceite-1.jpg', b'binary', content_type='image/jpeg'))
        second = ProductImageModel.objects.create(product=product, image=SimpleUploadedFile('aceite-2.jpg', b'binary', content_type='image/jpeg'))

        dtos = ProductImageModelDTOFactory.build_many([first, second])

        self.assertEqual(len(dtos), 2)
        self.assertIn('aceite-1', dtos[0].image_name)
        self.assertIn('aceite-2', dtos[1].image_name)
        self.assertTrue(dtos[0].image_name.endswith('.jpg'))
        self.assertTrue(dtos[1].image_name.endswith('.jpg'))
