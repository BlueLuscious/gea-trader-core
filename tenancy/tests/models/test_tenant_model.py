""" Model tests for tenant persistence. """

from uuid import UUID
from core.testing.base import LoggedTestCase
from tenancy.models import TenantModel


class TestTenantModel(LoggedTestCase):
    """ Verify tenant persistence and representation. """

    def test_string_representation_uses_tenant_name(self) -> None:
        """ Verify the tenant string representation stays human-friendly. """
        tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")

        self.assertEqual("GEA Center", str(tenant))
        self.assertIsInstance(tenant.pk, UUID)

    def test_optional_contact_fields_persist_on_the_tenant(self) -> None:
        """ Verify tenant operational contact metadata persists independently from visual branding. """
        tenant = TenantModel.objects.create(
            name="GEA Center",
            slug="gea-center",
            business_email="hello@gea-center.test",
            support_email="support@gea-center.test",
            phone_number="+54 11 5555 1234",
            website_url="https://gea-center.test",
        )

        self.assertEqual("hello@gea-center.test", tenant.business_email)
        self.assertEqual("support@gea-center.test", tenant.support_email)
        self.assertEqual("+54 11 5555 1234", tenant.phone_number)
        self.assertEqual("https://gea-center.test", tenant.website_url)
