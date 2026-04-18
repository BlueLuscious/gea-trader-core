""" Model tests for tenant memberships. """

from django.db import IntegrityError
from core.testing.base import LoggedTestCase
from accounts.models import UserModel
from tenancy.choices import TenantRole
from tenancy.models import TenantMembershipModel, TenantModel


class TestTenantMembershipModel(LoggedTestCase):
    """ Verify tenant membership persistence rules. """

    def setUp(self) -> None:
        """ Create reusable tenant and users for membership tests. """
        self.tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.user = UserModel.objects.create_user(username="lucio", password="test-pass")

    def test_membership_string_representation_prefers_user_tenant_and_role(self) -> None:
        """ Verify the tenant membership string representation stays admin-friendly. """
        membership = TenantMembershipModel.objects.create(
            tenant=self.tenant,
            user=self.user,
            role=TenantRole.OWNER,
        )

        self.assertIn("lucio", str(membership))
        self.assertIn("GEA Center", str(membership))
        self.assertIn(TenantRole.OWNER, str(membership))

    def test_membership_enforces_unique_user_per_tenant(self) -> None:
        """ Verify one user cannot be attached twice to the same tenant. """
        TenantMembershipModel.objects.create(tenant=self.tenant, user=self.user)

        with self.assertRaises(IntegrityError):
            TenantMembershipModel.objects.create(tenant=self.tenant, user=self.user)

    def test_membership_allows_only_one_primary_tenant_per_user(self) -> None:
        """ Verify one user keeps only one primary tenant membership. """
        other_tenant = TenantModel.objects.create(name="Other Center", slug="other-center")
        TenantMembershipModel.objects.create(tenant=self.tenant, user=self.user, is_primary=True)

        with self.assertRaises(IntegrityError):
            TenantMembershipModel.objects.create(tenant=other_tenant, user=self.user, is_primary=True)
