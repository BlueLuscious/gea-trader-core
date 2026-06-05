""" Tests for request-time active tenant resolution. """

from unittest.mock import patch
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponse
from accounts.models import UserModel
from core.testing.base import LoggedTestCase
from tenancy.runtime import ActiveTenantContext
from tenancy.middleware.active_tenant_middleware import ActiveTenantMiddleware
from tenancy.models import TenantMembershipModel, TenantModel


class TestActiveTenantMiddleware(LoggedTestCase):
    """ Verify middleware-based active tenant resolution. """

    def setUp(self) -> None:
        """ Create reusable users and tenants for middleware tests. """
        self.user = UserModel.objects.create_user(username="lucio", password="test-pass")
        self.primary_tenant = TenantModel.objects.create(name="GEA Center", slug="gea-center")
        self.secondary_tenant = TenantModel.objects.create(name="North Center", slug="north-center")
        TenantMembershipModel.objects.create(
            tenant=self.primary_tenant,
            user=self.user,
            is_primary=True,
        )
        TenantMembershipModel.objects.create(
            tenant=self.secondary_tenant,
            user=self.user,
            is_primary=False,
        )
        self.middleware = ActiveTenantMiddleware(lambda request: HttpResponse("ok"))

    def _build_request(self, path: str = "/owner-admin/") -> HttpRequest:
        """ Build a request with an attached session.

        Args:
            path: Request path.

        Returns:
            HttpRequest: Request ready for middleware execution.
        """
        request = HttpRequest()
        request.path = path
        request.path_info = path
        SessionMiddleware(lambda req: HttpResponse("ok")).process_request(request)
        request.session.save()
        return request

    def test_middleware_falls_back_to_primary_tenant(self) -> None:
        """ Verify the middleware uses the primary tenant when the session has none. """
        request = self._build_request()
        request.user = self.user

        with patch("tenancy.middleware.active_tenant_middleware.logger.info") as logger_info_mock:
            self.middleware(request)

        self.assertEqual(self.primary_tenant, request.tenant)
        self.assertEqual(str(self.primary_tenant.pk), request.session["active_tenant_id"])
        logger_info_mock.assert_called_once()

    def test_middleware_keeps_session_tenant_when_membership_is_valid(self) -> None:
        """ Verify the middleware preserves a session-selected tenant when the user still belongs to it. """
        request = self._build_request()
        request.user = self.user
        request.session["active_tenant_id"] = str(self.secondary_tenant.pk)

        self.middleware(request)

        self.assertEqual(self.secondary_tenant, request.tenant)

    def test_middleware_clears_active_tenant_for_anonymous_users(self) -> None:
        """ Verify the middleware clears tenant state for anonymous requests. """
        request = self._build_request()
        request.user = type("AnonymousUserLike", (), {"is_authenticated": False})()
        request.session["active_tenant_id"] = str(self.primary_tenant.pk)

        with patch("tenancy.middleware.active_tenant_middleware.logger.info") as logger_info_mock:
            self.middleware(request)

        self.assertIsNone(request.tenant)
        self.assertNotIn("active_tenant_id", request.session)
        logger_info_mock.assert_called_once()

    def test_middleware_exposes_current_tenant_during_request_and_clears_it_afterwards(self) -> None:
        """ Verify the middleware sets the runtime tenant context only for the active request. """
        captured_tenant_names: list[str | None] = []
        middleware = ActiveTenantMiddleware(
            lambda request: captured_tenant_names.append(
                getattr(ActiveTenantContext.get(), "name", None)
            ) or HttpResponse("ok")
        )
        request = self._build_request()
        request.user = self.user

        middleware(request)

        self.assertEqual(["GEA Center"], captured_tenant_names)
        self.assertIsNone(ActiveTenantContext.get())

    def test_middleware_skips_resolution_outside_owner_admin(self) -> None:
        """ Verify global requests do not invoke the admin tenant resolver. """
        request = self._build_request("/serviceworker.js")
        request.user = self.user

        with patch("tenancy.middleware.active_tenant_middleware.ActiveTenantResolver.resolve") as resolve_mock:
            self.middleware(request)

        resolve_mock.assert_not_called()
        self.assertIsNone(request.tenant)
        self.assertNotIn("active_tenant_id", request.session)

    def test_middleware_resolves_for_localized_owner_admin_paths(self) -> None:
        """ Verify localized owner-admin URLs remain tenant-aware. """
        request = self._build_request("/en/owner-admin/")
        request.user = self.user

        self.middleware(request)

        self.assertEqual(self.primary_tenant, request.tenant)
