from core.testing.base import LoggedTestCase
from masterdata.models import BrandModel, CategoryModel
from tenancy.models import TenantModel


class TestMasterdataQuerySet(LoggedTestCase):
    """ Cover masterdata queryset helpers. """

    def _create_tenant(self, slug: str) -> TenantModel:
        """ Create a tenant for tenant-aware queryset tests.

        Args:
            slug: Stable tenant slug.

        Returns:
            TenantModel: Persisted tenant instance.
        """
        return TenantModel.objects.create(name=slug.replace("-", " ").title(), slug=slug)

    def test_brand_active_filters_inactive_rows(self) -> None:
        """ Verify BrandModelQuerySet.active filters by active flag. """
        tenant = self._create_tenant("brand-queryset")
        active_brand = BrandModel.objects.create(tenant=tenant, name="GEA", slug="gea", is_active=True)
        BrandModel.objects.create(tenant=tenant, name="Legacy", slug="legacy", is_active=False)

        queryset = BrandModel.objects.get_queryset().active()

        self.assertQuerySetEqual(queryset, [active_brand], transform=lambda instance: instance)

    def test_brand_for_tenant_filters_other_tenant_rows(self) -> None:
        """ Verify BrandModelQuerySet.for_tenant keeps only one tenant scope. """
        tenant = self._create_tenant("north-brand-queryset")
        other_tenant = self._create_tenant("south-brand-queryset")
        active_brand = BrandModel.objects.create(tenant=tenant, name="GEA", slug="gea", is_active=True)
        BrandModel.objects.create(tenant=other_tenant, name="Legacy", slug="legacy", is_active=True)

        queryset = BrandModel.objects.get_queryset().for_tenant(tenant)

        self.assertQuerySetEqual(queryset, [active_brand], transform=lambda instance: instance)

    def test_category_active_roots_can_chain(self) -> None:
        """ Verify CategoryModelQuerySet supports active and root chaining. """
        tenant = self._create_tenant("category-queryset")
        active_root = CategoryModel.objects.create(tenant=tenant, name="Industrial", slug="industrial", is_active=True)
        inactive_root = CategoryModel.objects.create(tenant=tenant, name="Legacy", slug="legacy", is_active=False)
        CategoryModel.objects.create(tenant=tenant, name="Lubricacion", slug="lubricacion", parent=active_root, is_active=True)

        queryset = CategoryModel.objects.get_queryset().active().roots()

        self.assertQuerySetEqual(queryset, [active_root], transform=lambda instance: instance)
        self.assertNotIn(inactive_root, list(queryset))

    def test_category_for_tenant_filters_other_tenant_rows(self) -> None:
        """ Verify CategoryModelQuerySet.for_tenant keeps only one tenant scope. """
        tenant = self._create_tenant("north-category-queryset")
        other_tenant = self._create_tenant("south-category-queryset")
        active_root = CategoryModel.objects.create(tenant=tenant, name="Industrial", slug="industrial", is_active=True)
        CategoryModel.objects.create(tenant=other_tenant, name="Legacy", slug="legacy", is_active=True)

        queryset = CategoryModel.objects.get_queryset().for_tenant(tenant)

        self.assertQuerySetEqual(queryset, [active_root], transform=lambda instance: instance)
