from core.testing.base import LoggedTestCase
from masterdata.models import BrandModel, CategoryModel
from tenancy.models import TenantModel


class TestMasterdataManager(LoggedTestCase):
    """ Cover masterdata manager helpers. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for manager ownership tests.

        Args:
            slug: Stable tenant slug.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_brand_active_returns_only_active_brands(self) -> None:
        """ Verify the active brand manager helper filters inactive records. """
        tenant = self._create_tenant("brand-manager")
        active_brand = BrandModel.objects.create(tenant=tenant, name="GEA", slug="gea", is_active=True)
        BrandModel.objects.create(tenant=tenant, name="Old", slug="old", is_active=False)

        self.assertQuerySetEqual(BrandModel.objects.active(), [active_brand], transform=lambda instance: instance)

    def test_brand_for_tenant_returns_only_that_tenants_brands(self) -> None:
        """ Verify the tenant-aware brand manager helper filters other tenants. """
        tenant = self._create_tenant("north-brand-manager")
        other_tenant = self._create_tenant("south-brand-manager")
        active_brand = BrandModel.objects.create(tenant=tenant, name="GEA", slug="gea", is_active=True)
        BrandModel.objects.create(tenant=other_tenant, name="Old", slug="old", is_active=True)

        self.assertQuerySetEqual(BrandModel.objects.for_tenant(tenant), [active_brand], transform=lambda instance: instance)

    def test_category_roots_returns_only_root_categories(self) -> None:
        """ Verify the roots category manager helper filters child categories. """
        tenant = self._create_tenant("category-manager")
        root = CategoryModel.objects.create(tenant=tenant, name="Industrial", slug="industrial")
        CategoryModel.objects.create(tenant=tenant, name="Lubricacion", slug="lubricacion", parent=root)

        self.assertQuerySetEqual(CategoryModel.objects.roots(), [root], transform=lambda instance: instance)

    def test_category_for_tenant_returns_only_that_tenants_categories(self) -> None:
        """ Verify the tenant-aware category manager helper filters other tenants. """
        tenant = self._create_tenant("north-category-manager")
        other_tenant = self._create_tenant("south-category-manager")
        root = CategoryModel.objects.create(tenant=tenant, name="Industrial", slug="industrial")
        CategoryModel.objects.create(tenant=other_tenant, name="Lubricacion", slug="lubricacion")

        self.assertQuerySetEqual(CategoryModel.objects.for_tenant(tenant), [root], transform=lambda instance: instance)

    def test_category_featured_returns_only_featured_categories(self) -> None:
        """ Verify the featured category manager helper filters non-featured rows. """
        tenant = self._create_tenant("featured-category-manager")
        featured_root = CategoryModel.objects.create(
            tenant=tenant,
            name="Industrial",
            slug="industrial",
            is_featured=True,
        )
        CategoryModel.objects.create(
            tenant=tenant,
            name="Lubricacion",
            slug="lubricacion",
            is_featured=False,
        )

        self.assertQuerySetEqual(
            CategoryModel.objects.featured(),
            [featured_root],
            transform=lambda instance: instance,
        )
