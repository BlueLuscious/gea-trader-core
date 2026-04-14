""" Tests for admin site Unfold configuration resolution. """

from django.templatetags.static import static
from django.test import RequestFactory
from tenancy.models import TenantModel
from core.adminsites.admin_namespace import AdminNamespace
from core.adminsites.site_instances import master_admin_site
from core.adminsites.site_instances import owner_admin_site
from core.adminsites.sites.master_admin_site import MasterAdminSite
from core.adminsites.unfold import AdminSiteUnfoldCallbacks
from core.adminsites.unfold import AdminSiteUnfoldSettings
from core.testing.base import LoggedSimpleTestCase


class TestAdminSitesUnfold(LoggedSimpleTestCase):
    """ Cover request-based Unfold configuration for custom admin sites. """

    def setUp(self) -> None:
        """ Create the request factory used by the tests. """
        self.request_factory = RequestFactory()

    @staticmethod
    def build_file(url: str) -> object:
        """ Build a minimal file-like object exposing one ``url`` attribute.

        Args:
            url: Asset URL returned by the fake file.

        Returns:
            object: File-like object used in branding tests.
        """
        return type("BrandingFile", (), {"url": url})()

    def test_build_admin_site_unfold_settings_uses_site_metadata_for_static_values(self) -> None:
        """ Verify the generated settings dictionary reuses static metadata from the site class. """
        request = self.request_factory.get("/admin/")
        settings_dict = AdminSiteUnfoldSettings.for_namespace(AdminNamespace.MASTER).build()

        self.assertEqual(settings_dict["SITE_TITLE"](request), MasterAdminSite.get_site_title(request))
        self.assertEqual(settings_dict["SITE_HEADER"](request), MasterAdminSite.get_site_header(request))
        self.assertEqual(settings_dict["SITE_SUBHEADER"](request), MasterAdminSite.get_site_subheader(request))
        self.assertEqual(settings_dict["SITE_LOGO"](request), MasterAdminSite.get_site_logo(request))
        self.assertEqual(settings_dict["SITE_ICON"](request), MasterAdminSite.get_site_icon(request))
        self.assertEqual(settings_dict["SITE_SYMBOL"](request), MasterAdminSite.get_site_symbol(request))
        self.assertEqual(settings_dict["SITE_FAVICONS"](request), MasterAdminSite.get_site_favicons(request))
        self.assertEqual(settings_dict["SITE_URL"](request), MasterAdminSite.get_site_url(request))
        self.assertEqual(settings_dict["ENVIRONMENT"](request), MasterAdminSite.get_environment(request))
        self.assertEqual(settings_dict["LOGIN"]["image"](request), MasterAdminSite.get_login_image(request))

    def test_build_admin_site_unfold_settings_keeps_dynamic_sidebar_and_assets(self) -> None:
        """ Verify the generated settings dictionary keeps request-aware hooks only where needed. """
        settings_dict = AdminSiteUnfoldSettings.for_namespace(AdminNamespace.MASTER).build()

        self.assertEqual(settings_dict["SITE_TITLE"].__name__, "site_title")
        self.assertEqual(settings_dict["SITE_HEADER"].__name__, "site_header")
        self.assertEqual(settings_dict["SITE_SUBHEADER"].__name__, "site_subheader")
        self.assertEqual(settings_dict["SITE_LOGO"].__name__, "site_logo")
        self.assertEqual(settings_dict["SITE_ICON"].__name__, "site_icon")
        self.assertEqual(settings_dict["SITE_SYMBOL"].__name__, "site_symbol")
        self.assertEqual(settings_dict["SITE_FAVICONS"].__name__, "site_favicons")
        self.assertEqual(settings_dict["SITE_URL"].__name__, "site_url")
        self.assertEqual(settings_dict["ENVIRONMENT"].__name__, "environment")
        self.assertEqual(settings_dict["LOGIN"]["image"].__name__, "login_image")
        self.assertEqual(settings_dict["SITE_DROPDOWN"].__name__, "site_dropdown")
        self.assertEqual(settings_dict["SIDEBAR"]["navigation"].__name__, "sidebar_navigation")
        self.assertEqual(settings_dict["SCRIPTS"].__name__, "scripts")
        self.assertEqual(settings_dict["STYLES"].__name__, "styles")
        self.assertTrue(settings_dict["SIDEBAR"]["show_all_applications"](self.request_factory.get("/admin/")))

    def test_dynamic_callbacks_dispatch_to_owner_site_instance(self) -> None:
        """ Verify dynamic callbacks resolve the owner admin site instance from the request namespace. """
        membership = type(
            "Membership",
            (),
            {
                "role": "owner",
                "get_role_display": lambda self: "Owner",
            },
        )()
        tenant_memberships = type(
            "TenantMemberships",
            (),
            {
                "filter": lambda self, **kwargs: type("QuerySet", (), {"first": lambda self: membership})(),
            },
        )()
        branding = type(
            "Branding",
            (),
            {
                "display_name": "GEA Trader",
                "logo_light": self.build_file("/media/logo-light.png"),
                "logo_dark": self.build_file("/media/logo-dark.png"),
                "icon_light": self.build_file("/media/icon-light.png"),
                "icon_dark": self.build_file("/media/icon-dark.png"),
                "favicon_light": self.build_file("/media/favicon-light.png"),
                "favicon_dark": self.build_file("/media/favicon-dark.png"),
            },
        )()
        request = self.request_factory.get("/owner-admin/")
        request.user = type(
            "OwnerUser",
            (),
            {
                "is_active": True,
                "is_superuser": False,
                "is_staff": True,
                "has_module_perms": lambda self, app_label: True,
                "has_perm": lambda self, perm: True,
                "tenant_memberships": tenant_memberships,
            },
        )()
        request.tenant = TenantModel(name="GEA Lubricantes", slug="gea-lubricantes")
        request.tenant._state.fields_cache["branding"] = branding
        request.resolver_match = type("ResolverMatch", (), {"namespace": owner_admin_site.name})()

        self.assertEqual(AdminSiteUnfoldCallbacks.site_title(request), owner_admin_site.get_site_title(request))
        self.assertEqual(AdminSiteUnfoldCallbacks.site_header(request), owner_admin_site.get_site_header(request))
        self.assertEqual(AdminSiteUnfoldCallbacks.site_subheader(request), owner_admin_site.get_site_subheader(request))
        self.assertEqual(AdminSiteUnfoldCallbacks.site_logo(request), owner_admin_site.get_site_logo(request))
        self.assertEqual(AdminSiteUnfoldCallbacks.site_icon(request), owner_admin_site.get_site_icon(request))
        self.assertEqual(AdminSiteUnfoldCallbacks.site_symbol(request), owner_admin_site.get_site_symbol(request))
        self.assertEqual(AdminSiteUnfoldCallbacks.site_favicons(request), owner_admin_site.get_site_favicons(request))
        self.assertEqual(AdminSiteUnfoldCallbacks.site_url(request), owner_admin_site.get_site_url(request))
        self.assertEqual(AdminSiteUnfoldCallbacks.environment(request), owner_admin_site.get_environment(request))
        self.assertEqual(AdminSiteUnfoldCallbacks.login_image(request), owner_admin_site.get_login_image(request))
        self.assertEqual(AdminSiteUnfoldCallbacks.site_dropdown(request), owner_admin_site.get_site_dropdown(request))
        self.assertEqual(AdminSiteUnfoldCallbacks.show_search(request), owner_admin_site.get_show_sidebar_search(request))
        self.assertEqual(
            AdminSiteUnfoldCallbacks.show_all_applications(request),
            owner_admin_site.get_show_all_applications(request),
        )
        callback_navigation = AdminSiteUnfoldCallbacks.sidebar_navigation(request)
        site_navigation = owner_admin_site.get_sidebar_navigation(request)

        self.assertEqual([group["title"] for group in callback_navigation], [group["title"] for group in site_navigation])
        self.assertEqual(
            [item["title"] for group in callback_navigation for item in group["items"]],
            [item["title"] for group in site_navigation for item in group["items"]],
        )
        self.assertEqual(
            [item["link"] for group in callback_navigation for item in group["items"]],
            [item["link"] for group in site_navigation for item in group["items"]],
        )
        self.assertEqual(AdminSiteUnfoldCallbacks.scripts(request), owner_admin_site.get_scripts(request))
        self.assertEqual(AdminSiteUnfoldCallbacks.styles(request), owner_admin_site.get_styles(request))

    def test_owner_admin_site_metadata_prefers_the_active_tenant(self) -> None:
        """ Verify the owner admin metadata uses the active tenant when one is available. """
        request = self.request_factory.get("/owner-admin/")
        request.tenant = TenantModel(name="GEA Lubricantes", slug="gea-lubricantes")

        self.assertEqual("GEA Lubricantes", owner_admin_site.get_site_title(request))

    def test_owner_admin_branding_prefers_display_name_for_title_and_header(self) -> None:
        """ Verify owner admin title and header prefer tenant branding display names. """
        request = self.request_factory.get("/owner-admin/")
        request.tenant = TenantModel(name="GEA Lubricantes", slug="gea-lubricantes")
        request.tenant._state.fields_cache["branding"] = type("Branding", (), {"display_name": "GEA Trader"})()

        self.assertEqual("GEA Trader", owner_admin_site.get_site_title(request))
        self.assertEqual("GEA Trader", owner_admin_site.get_site_header(request))

    def test_owner_admin_branding_builds_logo_icon_and_favicons(self) -> None:
        """ Verify owner admin exposes tenant branding assets in the shapes expected by Unfold. """
        request = self.request_factory.get("/owner-admin/")
        request.tenant = TenantModel(name="GEA Lubricantes", slug="gea-lubricantes")
        request.tenant._state.fields_cache["branding"] = type(
            "Branding",
            (),
            {
                "logo_light": self.build_file("/media/logo-light.png"),
                "logo_dark": self.build_file("/media/logo-dark.png"),
                "icon_light": self.build_file("/media/icon-light.png"),
                "icon_dark": self.build_file("/media/icon-dark.png"),
                "favicon_light": self.build_file("/media/favicon-light.png"),
                "favicon_dark": self.build_file("/media/favicon-dark.png"),
            },
        )()

        self.assertEqual(
            {
                "light": "/media/logo-light.png",
                "dark": "/media/logo-dark.png",
            },
            owner_admin_site.get_site_logo(request),
        )
        self.assertEqual(
            {
                "light": "/media/icon-light.png",
                "dark": "/media/icon-dark.png",
            },
            owner_admin_site.get_site_icon(request),
        )
        self.assertEqual(
            [
                {"href": "/media/favicon-light.png", "rel": "icon", "type": "image/png"},
                {"href": "/media/favicon-dark.png", "rel": "icon", "type": "image/png"},
            ],
            owner_admin_site.get_site_favicons(request),
        )

    def test_owner_admin_each_context_includes_script_assets_from_callable_settings(self) -> None:
        """ Verify owner admin scripts configured through Unfold callbacks reach the template context. """
        request = self.request_factory.get("/owner-admin/")
        request.user = type(
            "AnonymousLikeUser",
            (),
            {
                "is_active": False,
                "is_staff": False,
                "is_authenticated": False,
                "has_module_perms": lambda self, app_label: False,
                "has_perm": lambda self, perm: False,
            },
        )()
        request.resolver_match = type("ResolverMatch", (), {"namespace": owner_admin_site.name})()

        context = owner_admin_site.each_context(request)

        self.assertIn(
            static("tenancy/admin/owner/owner_tenant_favicons.js"),
            context["scripts"],
        )

    def test_owner_admin_environment_uses_the_active_membership_role(self) -> None:
        """ Verify the owner admin environment badge reflects the active tenant role. """
        request = self.request_factory.get("/owner-admin/")
        request.tenant = TenantModel(name="GEA Lubricantes", slug="gea-lubricantes")
        membership = type(
            "Membership",
            (),
            {
                "role": "owner",
                "get_role_display": lambda self: "Owner",
            },
        )()
        tenant_memberships = type(
            "TenantMemberships",
            (),
            {
                "filter": lambda self, **kwargs: type("QuerySet", (), {"first": lambda self: membership})(),
            },
        )()
        request.user = type("OwnerUser", (), {"tenant_memberships": tenant_memberships})()

        self.assertEqual(["Owner", "primary"], owner_admin_site.get_environment(request))

    def test_owner_admin_sidebar_navigation_includes_curated_links(self) -> None:
        """ Verify the owner admin sidebar exposes the curated users, products, and quotes entries. """
        request = self.request_factory.get("/owner-admin/")
        request.user = type(
            "OwnerUser",
            (),
            {
                "is_active": True,
                "is_superuser": False,
                "is_staff": True,
                "has_module_perms": lambda self, app_label: True,
                "has_perm": lambda self, perm: True,
            },
        )()
        request.tenant = TenantModel(name="GEA Lubricantes", slug="gea-lubricantes")
        navigation = owner_admin_site.get_sidebar_navigation(request)

        item_links = {
            item["link"]
            for group in navigation
            for item in group["items"]
        }

        self.assertIn("/owner-admin/accounts/usermodel/", item_links)
        self.assertIn("/owner-admin/catalog/productmodel/", item_links)
        self.assertIn("/owner-admin/quotation/quotemodel/", item_links)

    def test_master_admin_sidebar_navigation_includes_users_groups_and_tenancy(self) -> None:
        """ Verify the master admin sidebar includes account and tenancy management links. """
        request = self.request_factory.get("/admin/")
        request.user = type(
            "SuperUser",
            (),
            {
                "is_active": True,
                "is_superuser": True,
                "is_staff": True,
                "has_module_perms": lambda self, app_label: True,
                "has_perm": lambda self, perm: True,
            },
        )()
        navigation = master_admin_site.get_sidebar_navigation(request)

        item_links = {
            item["link"]
            for group in navigation
            for item in group["items"]
        }

        self.assertIn("/admin/accounts/usermodel/", item_links)
        self.assertIn("/admin/auth/group/", item_links)
        self.assertIn("/admin/tenancy/tenantmodel/", item_links)
        self.assertIn("/admin/tenancy/tenantgroupmodel/", item_links)
        self.assertIn("/admin/tenancy/tenantmembershipmodel/", item_links)
