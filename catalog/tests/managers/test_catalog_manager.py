from django.core.files.uploadedfile import SimpleUploadedFile
from core.testing.base import LoggedTestCase
from catalog.models import ProductImageModel, ProductModel, ProductVariantModel
from masterdata.models import BrandModel, CategoryModel
from tenancy.models import TenantModel


class TestCatalogManager(LoggedTestCase):
    """ Cover catalog manager helpers. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for manager ownership tests.

        Args:
            slug: Stable slug for the tenant.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_product_manager_helpers_filter_and_select_related(self) -> None:
        """ Verify product manager helpers expose active, featured and related loading behavior. """
        tenant = self._create_tenant("north")
        brand = BrandModel.objects.create(tenant=tenant, name="GEA", slug="gea")
        category = CategoryModel.objects.create(tenant=tenant, name="Lubricacion", slug="lubricacion")
        active_featured = ProductModel.objects.create(tenant=tenant, brand=brand, category=category, name="Activo", slug="activo", is_active=True, is_featured=True, requires_quote=True)
        ProductModel.objects.create(tenant=tenant, name="Inactivo", slug="inactivo", is_active=False, is_featured=False, requires_quote=False)

        self.assertQuerySetEqual(ProductModel.objects.for_tenant(tenant).active(), [active_featured], transform=lambda instance: instance)
        self.assertQuerySetEqual(ProductModel.objects.for_tenant(tenant).featured(), [active_featured], transform=lambda instance: instance)
        self.assertQuerySetEqual(ProductModel.objects.for_tenant(tenant).requiring_quote(), [active_featured], transform=lambda instance: instance)
        self.assertIn('brand', ProductModel.objects.with_related().query.select_related)
        self.assertIn('category', ProductModel.objects.with_related().query.select_related)

    def test_variant_and_image_helpers_work_with_tenant_scoping(self) -> None:
        """ Verify variant and image manager helpers expose tenant-scoped filtered subsets. """
        tenant = self._create_tenant("north")
        other_tenant = self._create_tenant("south")
        product = ProductModel.objects.create(tenant=tenant, name="Bomba", slug="bomba")
        other_product = ProductModel.objects.create(tenant=other_tenant, name="Bomba Sur", slug="bomba-sur")
        default_variant = ProductVariantModel.objects.create(product=product, sku="BOM-001", is_default=True, is_active=True)
        secondary_variant = ProductVariantModel.objects.create(product=product, sku="BOM-002", is_default=False, is_active=False)
        ProductVariantModel.objects.create(product=other_product, sku="BOM-SUR-001", is_default=True, is_active=True)
        primary_image = ProductImageModel.objects.create(product=product, image=SimpleUploadedFile("bomba.jpg", b"binary", content_type="image/jpeg"), sort_order=2, is_primary=True)
        ProductImageModel.objects.create(product=product, image=SimpleUploadedFile("bomba-2.jpg", b"binary", content_type="image/jpeg"), sort_order=1, is_primary=False)
        ProductImageModel.objects.create(product=other_product, image=SimpleUploadedFile("bomba-sur.jpg", b"binary", content_type="image/jpeg"), sort_order=0, is_primary=True)

        self.assertQuerySetEqual(ProductVariantModel.objects.for_tenant(tenant).defaults(), [default_variant], transform=lambda instance: instance)
        self.assertQuerySetEqual(ProductVariantModel.objects.for_tenant(tenant).for_product(product), [default_variant, secondary_variant], transform=lambda instance: instance)
        self.assertQuerySetEqual(ProductImageModel.objects.for_tenant(tenant).primary(), [primary_image], transform=lambda instance: instance)
        self.assertEqual(list(ProductImageModel.objects.for_tenant(tenant).ordered().values_list('sort_order', flat=True)), [1, 2])
