from django.core.files.uploadedfile import SimpleUploadedFile
from core.testing.base import LoggedTestCase
from catalog.models import ProductImageModel, ProductModel, ProductVariantModel
from masterdata.models import BrandModel, CategoryModel


class TestCatalogModel(LoggedTestCase):
    """ Cover catalog model behavior. """

    def test_product_variant_and_image_relationships(self) -> None:
        """ Verify catalog relations between product, variant and image. """
        brand = BrandModel.objects.create(name="GEA", slug="gea")
        category = CategoryModel.objects.create(name="Lubricacion", slug="lubricacion")
        product = ProductModel.objects.create(brand=brand, category=category, name="Aceite termico", slug="aceite-termico")
        variant = ProductVariantModel.objects.create(product=product, sku="ACE-001", attributes_json={"viscosidad": "46"}, is_default=True)
        image = ProductImageModel.objects.create(product=product, variant=variant, image=SimpleUploadedFile("aceite.jpg", b"binary", content_type="image/jpeg"), alt_text="Aceite termico", is_primary=True)

        self.assertEqual(variant.product, product)
        self.assertEqual(image.product, product)
        self.assertEqual(image.variant, variant)

    def test_string_representations_prefer_human_labels(self) -> None:
        """ Verify catalog model string representations are user friendly. """
        product = ProductModel.objects.create(name="Bomba", slug="bomba")
        variant = ProductVariantModel.objects.create(product=product, name="Linea A", sku="BOM-001")
        image = ProductImageModel.objects.create(product=product, image=SimpleUploadedFile("bomba.jpg", b"binary", content_type="image/jpeg"), alt_text="Bomba frontal")

        self.assertEqual(str(product), "Bomba")
        self.assertEqual(str(variant), "Linea A")
        self.assertEqual(str(image), "Bomba frontal")
