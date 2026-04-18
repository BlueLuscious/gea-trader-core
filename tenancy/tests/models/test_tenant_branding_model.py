""" Model tests for tenant branding persistence. """

from core.testing.base import LoggedTestCase
from tenancy.models import TenantBrandingModel, TenantModel


class TestTenantBrandingModel(LoggedTestCase):
    """ Verify tenant branding persistence and representation. """

    def test_string_representation_prefers_display_name(self) -> None:
        """ Verify the branding string representation uses the configured display name when available. """
        tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        branding = TenantBrandingModel.objects.create(tenant=tenant, display_name="GEA Trader")

        self.assertEqual("GEA Trader", str(branding))

    def test_string_representation_falls_back_to_tenant_name(self) -> None:
        """ Verify the branding string representation falls back to the tenant when no display name exists. """
        tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        branding = TenantBrandingModel.objects.create(tenant=tenant)

        self.assertEqual("GEA Center", str(branding))
