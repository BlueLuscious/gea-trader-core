""" Manager tests for tenant branding access helpers. """

from core.testing.base import LoggedTestCase
from tenancy.models import TenantBrandingModel, TenantModel


class TestTenantBrandingModelManager(LoggedTestCase):
    """ Verify the tenant-branding manager exposes the expected shortcuts. """

    def setUp(self) -> None:
        """ Create reusable tenant branding rows for manager tests. """
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.other_tenant = TenantModel.objects.create(name="Quinoto", slug="quinoto")
        self.configured_branding = TenantBrandingModel.objects.create(
            tenant=self.tenant,
            display_name="GEA Trader",
        )
        TenantBrandingModel.objects.create(tenant=self.other_tenant)

    def test_for_tenant_returns_branding_for_the_provided_tenant(self) -> None:
        """ Verify the tenant-branding manager exposes the tenant-scoped queryset shortcut. """
        self.assertEqual([self.configured_branding], list(TenantBrandingModel.objects.for_tenant(self.tenant)))

    def test_configured_returns_branding_rows_with_visible_data(self) -> None:
        """ Verify the tenant-branding manager exposes only branding rows that already contain configured values. """
        self.assertEqual([self.configured_branding], list(TenantBrandingModel.objects.configured()))

    def test_with_tenant_selects_the_related_tenant(self) -> None:
        """ Verify the tenant-branding manager exposes the eager-loading shortcut for the related tenant. """
        queryset = TenantBrandingModel.objects.with_tenant()

        self.assertIn("tenant", queryset.query.select_related)
