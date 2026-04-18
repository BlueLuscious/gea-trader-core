""" Tests for owner-delegable permission resolution. """

from unittest.mock import patch
from django.contrib.auth.models import Permission
from core.testing.base import LoggedTestCase
from accounts.models import UserModel
from accounts.services import OwnerDelegablePermissionResolver
from tenancy.choices import TenantRole
from tenancy.models import TenantMembershipModel, TenantModel


class TestOwnerDelegablePermissionResolver(LoggedTestCase):
    """ Verify owner-delegable permission resolution stays constrained. """

    def test_get_queryset_returns_all_permissions_already_held_by_the_owner(self) -> None:
        """ Verify the owner may delegate every permission already held by the actor. """
        owner = UserModel.objects.create_user(
            username="owner",
            password="test-pass",
            is_staff=True,
            is_active=True,
        )
        tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        TenantMembershipModel.objects.create(
            tenant=tenant,
            user=owner,
            role=TenantRole.OWNER,
            is_active=True,
            is_primary=True,
        )
        owner.user_permissions.set(
            Permission.objects.filter(
                codename__in=(
                    "view_usermodel",
                    "change_group",
                    "view_tenantgroupmodel",
                    "view_tenantmodel",
                )
            )
        )

        with patch("accounts.services.owner_delegable_permission_resolver.logger.info") as logger_info_mock:
            visible_codenames = list(
                OwnerDelegablePermissionResolver.get_queryset(owner, tenant).values_list("codename", flat=True)
            )

        self.assertIn("view_usermodel", visible_codenames)
        self.assertIn("change_group", visible_codenames)
        self.assertIn("view_tenantgroupmodel", visible_codenames)
        self.assertIn("view_tenantmodel", visible_codenames)
        logger_info_mock.assert_called_once()

    def test_get_queryset_returns_none_for_non_owner_membership(self) -> None:
        """ Verify non-owner tenant members cannot delegate any permissions. """
        user = UserModel.objects.create_user(
            username="operator",
            password="test-pass",
            is_staff=True,
            is_active=True,
        )
        tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        TenantMembershipModel.objects.create(
            tenant=tenant,
            user=user,
            role=TenantRole.MASTER,
            is_active=True,
            is_primary=True,
        )
        user.user_permissions.set(Permission.objects.filter(codename__in=("view_usermodel", "change_group")))

        with patch("accounts.services.owner_delegable_permission_resolver.logger.info") as logger_info_mock:
            self.assertEqual([], list(OwnerDelegablePermissionResolver.get_queryset(user, tenant)))

        logger_info_mock.assert_called_once()
