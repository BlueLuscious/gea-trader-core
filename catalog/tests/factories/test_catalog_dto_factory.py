from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile
from core.testing.base import LoggedTestCase
from catalog.dtos.factories import ProductImageModelDTOFactory, ProductModelDTOFactory, ProductVariantModelDTOFactory
from catalog.models import ProductImageModel, ProductModel, ProductVariantModel


class TestCatalogDTOFactory(LoggedTestCase):
    """ Cover catalog DTO factories. """

    def test_product_model_dto_factory_build_maps_fields(self) -> None:
        """ Verify ProductModelDTOFactory.build maps core product fields. """
        product = ProductModel.objects.create(name='Bomba', slug='bomba', sku_base='BOM', is_featured=True)

        dto = ProductModelDTOFactory.build(product)

        self.assertEqual(dto.id, product.id)
        self.assertEqual(dto.sku_base, 'BOM')
        self.assertTrue(dto.is_featured)

    def test_variant_factory_copies_attributes_json(self) -> None:
        """ Verify ProductVariantModelDTOFactory copies the attributes dictionary. """
        product = ProductModel.objects.create(name='Filtro', slug='filtro')
        variant = ProductVariantModel.objects.create(product=product, sku='FIL-001', attributes_json={'viscosidad': '46'}, price=Decimal('15.00'))

        dto = ProductVariantModelDTOFactory.build(variant)
        variant.attributes_json['viscosidad'] = '68'

        self.assertEqual(dto.attributes_json['viscosidad'], '46')
        self.assertEqual(dto.price, Decimal('15.00'))

    def test_image_factory_build_many_returns_expected_names(self) -> None:
        """ Verify ProductImageModelDTOFactory.build_many keeps image metadata. """
        product = ProductModel.objects.create(name='Aceite', slug='aceite')
        first = ProductImageModel.objects.create(product=product, image=SimpleUploadedFile('aceite-1.jpg', b'binary', content_type='image/jpeg'))
        second = ProductImageModel.objects.create(product=product, image=SimpleUploadedFile('aceite-2.jpg', b'binary', content_type='image/jpeg'))

        dtos = ProductImageModelDTOFactory.build_many([first, second])

        self.assertEqual(len(dtos), 2)
        self.assertIn('aceite-1', dtos[0].image_name)
        self.assertIn('aceite-2', dtos[1].image_name)
        self.assertTrue(dtos[0].image_name.endswith('.jpg'))
        self.assertTrue(dtos[1].image_name.endswith('.jpg'))
