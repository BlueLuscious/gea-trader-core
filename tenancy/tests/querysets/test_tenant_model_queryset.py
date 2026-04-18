""" QuerySet tests for tenant filters. """

from core.testing.base import LoggedTestCase
from accounts.models import UserModel
from tenancy.models import TenantMembershipModel, TenantModel


class TestTenantModelQuerySet(LoggedTestCase):
    """ Verify reusable tenant queryset helpers. """

    def setUp(self) -> None:
        """ Create reusable tenants and memberships for queryset tests. """
        self.user = UserModel.objects.create_user(username="lucio", password="test-pass")
        self.active_tenant = TenantModel.objects.create(name="Active Center", slug="active-center", is_active=True)
        self.inactive_tenant = TenantModel.objects.create(name="Inactive Center", slug="inactive-center", is_active=False)
        TenantMembershipModel.objects.create(tenant=self.active_tenant, user=self.user)

    def test_active_filters_only_active_tenants(self) -> None:
        """ Verify active tenants exclude inactive rows. """
        self.assertEqual([self.active_tenant], list(TenantModel.objects.active()))

    def test_for_user_returns_related_tenants(self) -> None:
        """ Verify tenant queryset can resolve all tenants linked to one user. """
        self.assertEqual([self.active_tenant], list(TenantModel.objects.for_user(self.user)))
