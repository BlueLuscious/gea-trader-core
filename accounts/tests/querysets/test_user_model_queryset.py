""" QuerySet tests for user access helpers. """

from core.testing.base import LoggedTestCase
from accounts.models import UserModel
from tenancy.models import TenantMembershipModel, TenantModel


class TestUserModelQuerySet(LoggedTestCase):
    """ Verify the user queryset exposes tenant-related filters. """

    def setUp(self) -> None:
        """ Create reusable users and tenants for queryset tests. """
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.user = UserModel.objects.create_user(username="lucio", password="test-pass")
        self.other_user = UserModel.objects.create_user(username="sofia", password="test-pass")
        TenantMembershipModel.objects.create(tenant=self.tenant, user=self.user)

    def test_for_tenant_filters_users_by_membership(self) -> None:
        """ Verify the queryset returns only users linked to the provided tenant. """
        self.assertEqual([self.user], list(UserModel.objects.all().for_tenant(self.tenant)))

    def test_with_tenants_prefetches_membership_relations(self) -> None:
        """ Verify the queryset prefetches tenant relations for later access. """
        queryset = UserModel.objects.all().with_tenants()

        self.assertIn("tenant_memberships__tenant", queryset._prefetch_related_lookups)
