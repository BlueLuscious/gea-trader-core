""" Manager tests for user access helpers. """

from core.testing.base import LoggedTestCase
from accounts.models import UserModel
from tenancy.models import TenantMembershipModel, TenantModel


class TestUserModelManager(LoggedTestCase):
    """ Verify the user manager exposes tenant-related shortcuts. """

    def setUp(self) -> None:
        """ Create reusable users and tenants for manager tests. """
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.user = UserModel.objects.create_user(username="lucio", password="test-pass")
        self.other_user = UserModel.objects.create_user(username="sofia", password="test-pass")
        TenantMembershipModel.objects.create(tenant=self.tenant, user=self.user)

    def test_for_tenant_returns_related_users(self) -> None:
        """ Verify the manager can resolve users linked to one tenant. """
        self.assertEqual([self.user], list(UserModel.objects.for_tenant(self.tenant)))

    def test_with_tenants_prefetches_membership_relations(self) -> None:
        """ Verify the manager can prefetch tenant relations for user queries. """
        queryset = UserModel.objects.with_tenants()

        self.assertIn("tenant_memberships__tenant", queryset._prefetch_related_lookups)
