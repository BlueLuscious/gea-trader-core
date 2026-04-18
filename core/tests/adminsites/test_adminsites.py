""" Tests for custom admin site permissions. """

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, override_settings
from django.utils.translation import gettext as _, override
from core.adminsites.sites.master_admin_site import MasterAdminSite
from core.adminsites.sites.owner_admin_site import OwnerAdminSite
from core.adminsites.unfold.admin_site_unfold_callbacks import AdminSiteUnfoldCallbacks
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

    def test_owner_admin_sidebar_navigation_includes_business_and_accounts_items_when_permissions_exist(self) -> None:
        """ Verify the owner admin sidebar exposes Business settings together with Users and Groups. """
        owner = type(
            "OwnerUser",
            (),
            {
                "is_active": True,
                "is_superuser": True,
                "is_staff": True,
                "is_authenticated": True,
                "has_perm": lambda self, perm: perm in {"accounts.view_usermodel", "auth.view_group"},
            },
        )()

        request = self.request_factory.get("/owner-admin/")
        request.user = owner
        request.tenant = object()

        navigation = self.owner_admin_site.get_sidebar_navigation(request)
        item_titles = [item["title"] for group in navigation for item in group["items"]]

        self.assertEqual([_("Settings"), _("Users"), _("Groups")], item_titles)

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

    def test_unfold_language_navigation_uses_translated_language_labels(self) -> None:
        """ Verify the Unfold language selector uses translated labels from settings. """
        request = self.request_factory.get("/owner-admin/")

        with override("es"):
            languages = AdminSiteUnfoldCallbacks.languages_navigation(request)
            self.assertEqual("Español", languages[0]["name_local"])
            self.assertEqual("Inglés", languages[1]["name_local"])

        with override("en"):
            languages = AdminSiteUnfoldCallbacks.languages_navigation(request)
            self.assertEqual("Spanish", languages[0]["name_local"])
            self.assertEqual("English", languages[1]["name_local"])

    @override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])
    def test_admin_language_switcher_strips_english_prefix_when_returning_to_spanish(self) -> None:
        """ Verify the custom language view returns to the unprefixed default admin URL. """
        response = self.client.post(
            "/i18n/admin-setlang/",
            {"language": "es", "next": "/en/owner-admin/"},
            follow=False,
        )

        self.assertEqual(302, response.status_code)
        self.assertEqual("/owner-admin/", response.headers["Location"])
        self.assertEqual("es", response.cookies["django_language"].value)

    @override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])
    def test_admin_language_switcher_adds_english_prefix_when_switching_from_spanish(self) -> None:
        """ Verify the custom language view adds the /en/ prefix for English admin URLs. """
        response = self.client.post(
            "/i18n/admin-setlang/",
            {"language": "en", "next": "/owner-admin/"},
            follow=False,
        )

        self.assertEqual(302, response.status_code)
        self.assertEqual("/en/owner-admin/", response.headers["Location"])
        self.assertEqual("en", response.cookies["django_language"].value)
