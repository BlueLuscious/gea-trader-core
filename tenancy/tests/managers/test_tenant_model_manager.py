""" Manager tests for tenant access helpers. """

from core.testing.base import LoggedTestCase
from accounts.models import UserModel
from tenancy.models import TenantMembershipModel, TenantModel


class TestTenantModelManager(LoggedTestCase):
    """ Verify the tenant manager exposes the expected shortcuts. """

    def setUp(self) -> None:
        """ Create reusable tenants and memberships for manager tests. """
        self.user = UserModel.objects.create_user(username="lucio", password="test-pass")
        self.active_tenant = TenantModel.objects.create(name="Active Center", slug="active-center", is_active=True)
        TenantMembershipModel.objects.create(tenant=self.active_tenant, user=self.user)
        TenantModel.objects.create(name="Inactive Center", slug="inactive-center", is_active=False)

    def test_active_returns_only_active_tenants(self) -> None:
        """ Verify the tenant manager exposes the active queryset shortcut. """
        self.assertEqual([self.active_tenant], list(TenantModel.objects.active()))

    def test_for_user_returns_related_tenants(self) -> None:
        """ Verify the tenant manager exposes the user-scoped queryset shortcut. """
        self.assertEqual([self.active_tenant], list(TenantModel.objects.for_user(self.user)))
