""" Tests for the base tenant access policy. """

from core.testing.base import LoggedTestCase
from accounts.models import UserModel
from tenancy.choices import TenantRole
from tenancy.models import TenantMembershipModel, TenantModel
from tenancy.access.tenant_access_policy import TenantAccessPolicy


class TestTenantAccessPolicy(LoggedTestCase):
    """ Verify tenant access checks stay aligned with memberships and roles. """

    def test_can_access_tenant_returns_true_for_active_member(self) -> None:
        """ Verify active tenant memberships may access the tenant context. """
        user = UserModel.objects.create_user(username="member", password="test-pass", is_active=True, is_staff=True)
        tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        TenantMembershipModel.objects.create(
            tenant=tenant,
            user=user,
            role=TenantRole.OPERATOR,
            is_active=True,
            is_primary=True,
        )

        self.assertTrue(TenantAccessPolicy.can_access_tenant(user, tenant))

    def test_has_role_returns_false_for_other_role(self) -> None:
        """ Verify role checks stay scoped to the requested tenant role. """
        user = UserModel.objects.create_user(username="operator", password="test-pass", is_active=True, is_staff=True)
        tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        TenantMembershipModel.objects.create(
            tenant=tenant,
            user=user,
            role=TenantRole.OPERATOR,
            is_active=True,
            is_primary=True,
        )

        self.assertFalse(TenantAccessPolicy.has_role(user, tenant, TenantRole.OWNER))

    def test_can_manage_tenant_returns_true_for_owner_members(self) -> None:
        """ Verify active owner memberships may manage the tenant. """
        user = UserModel.objects.create_user(username="owner", password="test-pass", is_active=True, is_staff=True)
        tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        TenantMembershipModel.objects.create(
            tenant=tenant,
            user=user,
            role=TenantRole.OWNER,
            is_active=True,
            is_primary=True,
        )

        self.assertTrue(TenantAccessPolicy.can_manage_tenant(user, tenant))
