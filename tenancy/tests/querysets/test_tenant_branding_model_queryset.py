""" QuerySet tests for tenant branding filters. """

from core.testing.base import LoggedTestCase
from tenancy.models import TenantBrandingModel, TenantModel


class TestTenantBrandingModelQuerySet(LoggedTestCase):
    """ Verify reusable tenant-branding queryset helpers. """

    def setUp(self) -> None:
        """ Create reusable tenant branding rows for queryset tests. """
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.other_tenant = TenantModel.objects.create(name="Quinoto", slug="quinoto")
        self.configured_branding = TenantBrandingModel.objects.create(
            tenant=self.tenant,
            display_name="GEA Trader",
        )
        self.empty_branding = TenantBrandingModel.objects.create(tenant=self.other_tenant)

    def test_for_tenant_returns_branding_for_the_requested_tenant(self) -> None:
        """ Verify the tenant-branding queryset can resolve the branding row for one tenant. """
        self.assertEqual([self.configured_branding], list(TenantBrandingModel.objects.for_tenant(self.tenant)))

    def test_configured_returns_only_rows_with_branding_data(self) -> None:
        """ Verify configured branding excludes empty branding rows. """
        self.assertEqual([self.configured_branding], list(TenantBrandingModel.objects.configured()))

    def test_with_tenant_selects_the_related_tenant(self) -> None:
        """ Verify the tenant-branding queryset eager-loads the related tenant. """
        queryset = TenantBrandingModel.objects.with_tenant()

        self.assertIn("tenant", queryset.query.select_related)
