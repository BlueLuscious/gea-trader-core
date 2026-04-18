""" Model tests for tenant persistence. """

from uuid import UUID
from cart.models import CartModel
from catalog.models import ProductModel
from core.testing.base import LoggedTestCase
from masterdata.models import BrandModel, CategoryModel
from quotation.models import QuoteModel
from tenancy.models import TenantBrandingModel, TenantModel


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

    def test_related_domain_accessors_expose_current_business_roots(self) -> None:
        """ Verify the tenant exposes reverse accessors for the current business-domain roots. """
        tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        branding = TenantBrandingModel.objects.create(tenant=tenant, display_name="GEA")
        brand = BrandModel.objects.create(tenant=tenant, name="GEA", slug="gea")
        category = CategoryModel.objects.create(tenant=tenant, name="Pumps", slug="pumps")
        product = ProductModel.objects.create(
            tenant=tenant,
            brand=brand,
            category=category,
            name="Pump",
            slug="pump",
        )
        cart = CartModel.objects.create(tenant=tenant, session_key="session-tenant")
        quote = QuoteModel.objects.create(tenant=tenant, cart=cart, customer_email="buyer@example.com")

        self.assertEqual(branding, tenant.branding)
        self.assertEqual([brand], list(tenant.brands.all()))
        self.assertEqual([category], list(tenant.categories.all()))
        self.assertEqual([product], list(tenant.products.all()))
        self.assertEqual([cart], list(tenant.carts.all()))
        self.assertEqual([quote], list(tenant.quotes.all()))
