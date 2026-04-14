from django.core.files.uploadedfile import SimpleUploadedFile
from core.testing.base import LoggedTestCase
from catalog.models import ProductImageModel, ProductModel, ProductVariantModel
from tenancy.models import TenantModel


class TestCatalogQuerySet(LoggedTestCase):
    """ Cover catalog queryset helpers. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for queryset ownership tests.

        Args:
            slug: Stable slug for the tenant.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_product_queryset_chains_active_featured_and_quote(self) -> None:
        """ Verify ProductModelQuerySet can chain its main filters. """
        tenant = self._create_tenant("north")
        matching = ProductModel.objects.create(tenant=tenant, name="Bomba", slug="bomba", is_active=True, is_featured=True, requires_quote=True)
        ProductModel.objects.create(tenant=tenant, name="Otro", slug="otro", is_active=True, is_featured=False, requires_quote=True)

        queryset = ProductModel.objects.get_queryset().for_tenant(tenant).active().featured().requiring_quote()

        self.assertQuerySetEqual(queryset, [matching], transform=lambda instance: instance)

    def test_variant_and_image_queryset_helpers_filter_by_tenant_and_order(self) -> None:
        """ Verify variant and image queryset helpers stay scoped to the owning tenant. """
        tenant = self._create_tenant("north")
        other_tenant = self._create_tenant("south")
        product = ProductModel.objects.create(tenant=tenant, name="Filtro", slug="filtro")
        other_product = ProductModel.objects.create(tenant=other_tenant, name="Filtro Sur", slug="filtro-sur")
        active_default = ProductVariantModel.objects.create(product=product, sku="FIL-001", is_default=True, is_active=True)
        ProductVariantModel.objects.create(product=product, sku="FIL-002", is_default=False, is_active=False)
        ProductVariantModel.objects.create(product=other_product, sku="FIL-SUR-001", is_default=True, is_active=True)
        ProductImageModel.objects.create(product=product, image=SimpleUploadedFile("filtro-2.jpg", b"binary", content_type="image/jpeg"), sort_order=2)
        ProductImageModel.objects.create(product=product, image=SimpleUploadedFile("filtro-1.jpg", b"binary", content_type="image/jpeg"), sort_order=1)
        ProductImageModel.objects.create(product=other_product, image=SimpleUploadedFile("filtro-sur.jpg", b"binary", content_type="image/jpeg"), sort_order=0)

        variant_queryset = ProductVariantModel.objects.get_queryset().for_tenant(tenant).active().defaults().for_product(product)
        image_queryset = ProductImageModel.objects.get_queryset().for_tenant(tenant).ordered()

        self.assertQuerySetEqual(variant_queryset, [active_default], transform=lambda instance: instance)
        self.assertEqual(list(image_queryset.values_list('sort_order', flat=True)), [1, 2])
