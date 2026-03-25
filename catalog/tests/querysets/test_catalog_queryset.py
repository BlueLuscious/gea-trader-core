from django.core.files.uploadedfile import SimpleUploadedFile
from core.testing.base import LoggedTestCase
from catalog.models import ProductImageModel, ProductModel, ProductVariantModel


class TestCatalogQuerySet(LoggedTestCase):
    """ Cover catalog queryset helpers. """

    def test_product_queryset_chains_active_featured_and_quote(self) -> None:
        """ Verify ProductModelQuerySet can chain its main filters. """
        matching = ProductModel.objects.create(name="Bomba", slug="bomba", is_active=True, is_featured=True, requires_quote=True)
        ProductModel.objects.create(name="Otro", slug="otro", is_active=True, is_featured=False, requires_quote=True)

        queryset = ProductModel.objects.get_queryset().active().featured().requiring_quote()

        self.assertQuerySetEqual(queryset, [matching], transform=lambda instance: instance)

    def test_variant_and_image_queryset_helpers_filter_and_order(self) -> None:
        """ Verify variant and image queryset helpers return the expected subsets. """
        product = ProductModel.objects.create(name="Filtro", slug="filtro")
        active_default = ProductVariantModel.objects.create(product=product, sku="FIL-001", is_default=True, is_active=True)
        ProductVariantModel.objects.create(product=product, sku="FIL-002", is_default=False, is_active=False)
        ProductImageModel.objects.create(product=product, image=SimpleUploadedFile("filtro-2.jpg", b"binary", content_type="image/jpeg"), sort_order=2)
        ProductImageModel.objects.create(product=product, image=SimpleUploadedFile("filtro-1.jpg", b"binary", content_type="image/jpeg"), sort_order=1)

        variant_queryset = ProductVariantModel.objects.get_queryset().active().defaults().for_product(product)
        image_queryset = ProductImageModel.objects.get_queryset().ordered()

        self.assertQuerySetEqual(variant_queryset, [active_default], transform=lambda instance: instance)
        self.assertEqual(list(image_queryset.values_list('sort_order', flat=True)), [1, 2])
