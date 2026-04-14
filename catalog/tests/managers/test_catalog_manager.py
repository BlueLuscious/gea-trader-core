from django.core.files.uploadedfile import SimpleUploadedFile
from core.testing.base import LoggedTestCase
from catalog.models import ProductImageModel, ProductModel, ProductVariantModel
from masterdata.models import BrandModel, CategoryModel


class TestCatalogManager(LoggedTestCase):
    """ Cover catalog manager helpers. """

    def test_product_manager_helpers_filter_and_select_related(self) -> None:
        """ Verify product manager helpers expose active, featured and related loading behavior. """
        brand = BrandModel.objects.create(name="GEA", slug="gea")
        category = CategoryModel.objects.create(name="Lubricacion", slug="lubricacion")
        active_featured = ProductModel.objects.create(brand=brand, category=category, name="Activo", slug="activo", is_active=True, is_featured=True, requires_quote=True)
        ProductModel.objects.create(name="Inactivo", slug="inactivo", is_active=False, is_featured=False, requires_quote=False)

        self.assertQuerySetEqual(ProductModel.objects.active(), [active_featured], transform=lambda instance: instance)
        self.assertQuerySetEqual(ProductModel.objects.featured(), [active_featured], transform=lambda instance: instance)
        self.assertQuerySetEqual(ProductModel.objects.requiring_quote(), [active_featured], transform=lambda instance: instance)
        self.assertIn('brand', ProductModel.objects.with_related().query.select_related)
        self.assertIn('category', ProductModel.objects.with_related().query.select_related)

    def test_variant_and_image_helpers_work(self) -> None:
        """ Verify variant and image manager helpers expose their filtered subsets. """
        product = ProductModel.objects.create(name="Bomba", slug="bomba")
        default_variant = ProductVariantModel.objects.create(product=product, sku="BOM-001", is_default=True, is_active=True)
        secondary_variant = ProductVariantModel.objects.create(product=product, sku="BOM-002", is_default=False, is_active=False)
        primary_image = ProductImageModel.objects.create(product=product, image=SimpleUploadedFile("bomba.jpg", b"binary", content_type="image/jpeg"), sort_order=2, is_primary=True)
        ProductImageModel.objects.create(product=product, image=SimpleUploadedFile("bomba-2.jpg", b"binary", content_type="image/jpeg"), sort_order=1, is_primary=False)

        self.assertQuerySetEqual(ProductVariantModel.objects.defaults(), [default_variant], transform=lambda instance: instance)
        self.assertQuerySetEqual(ProductVariantModel.objects.for_product(product), [default_variant, secondary_variant], transform=lambda instance: instance)
        self.assertQuerySetEqual(ProductImageModel.objects.primary(), [primary_image], transform=lambda instance: instance)
        self.assertEqual(list(ProductImageModel.objects.ordered().values_list('sort_order', flat=True)), [1, 2])
