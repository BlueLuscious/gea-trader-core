""" Tests for custom admin site permissions. """

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from core.adminsites.sites.master_admin_site import MasterAdminSite
from core.adminsites.sites.owner_admin_site import OwnerAdminSite
from core.testing.base import LoggedSimpleTestCase


class TestAdminSites(LoggedSimpleTestCase):
    """ Cover permission behavior for custom admin sites. """

    def setUp(self) -> None:
        """ Create the request factory and site instances used by the tests. """
        self.request_factory = RequestFactory()
        self.master_admin_site = MasterAdminSite(name="test_master_admin")
        self.owner_admin_site = OwnerAdminSite(name="test_owner_admin")

    def test_master_admin_allows_active_superusers_only(self) -> None:
        """ Verify the master admin only allows active superusers. """
        superuser = type("SuperUser", (), {"is_active": True, "is_superuser": True, "is_staff": True})()
        owner = type("OwnerUser", (), {"is_active": True, "is_superuser": False, "is_staff": True})()

        master_request = self.request_factory.get("/admin/")
        master_request.user = superuser
        owner_request = self.request_factory.get("/admin/")
        owner_request.user = owner

        self.assertTrue(self.master_admin_site.has_permission(master_request))
        self.assertFalse(self.master_admin_site.has_permission(owner_request))

    def test_owner_admin_allows_active_staff_users(self) -> None:
        """ Verify the owner admin allows active staff users and superusers. """
        owner = type("OwnerUser", (), {"is_active": True, "is_superuser": False, "is_staff": True})()
        superuser = type("SuperUser", (), {"is_active": True, "is_superuser": True, "is_staff": True})()
        customer = type("CustomerUser", (), {"is_active": True, "is_superuser": False, "is_staff": False})()

        owner_request = self.request_factory.get("/owner-admin/")
        owner_request.user = owner
        superuser_request = self.request_factory.get("/owner-admin/")
        superuser_request.user = superuser
        customer_request = self.request_factory.get("/owner-admin/")
        customer_request.user = customer

        self.assertTrue(self.owner_admin_site.has_permission(owner_request))
        self.assertTrue(self.owner_admin_site.has_permission(superuser_request))
        self.assertFalse(self.owner_admin_site.has_permission(customer_request))

    def test_admin_sites_reject_anonymous_and_inactive_users(self) -> None:
        """ Verify both admin sites reject anonymous or inactive users. """
        anonymous_request = self.request_factory.get("/admin/")
        anonymous_request.user = AnonymousUser()
        inactive_staff = type("InactiveStaff", (), {"is_active": False, "is_superuser": False, "is_staff": True})()
        inactive_request = self.request_factory.get("/owner-admin/")
        inactive_request.user = inactive_staff

        self.assertFalse(self.master_admin_site.has_permission(anonymous_request))
        self.assertFalse(self.owner_admin_site.has_permission(anonymous_request))
        self.assertFalse(self.master_admin_site.has_permission(inactive_request))
        self.assertFalse(self.owner_admin_site.has_permission(inactive_request))
