""" Class-based view for explicit active-tenant switching. """

from uuid import UUID
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from tenancy.switching.active_tenant_switcher import ActiveTenantSwitcher

logger = logging.getLogger(__name__)


class SwitchActiveTenantView(LoginRequiredMixin, View):
    """ Switch the active tenant for the current authenticated user through one GET request. """

    http_method_names = ["get"]

    def get(self, request: HttpRequest, tenant_id: UUID) -> HttpResponse:
        """ Switch the active tenant for the current authenticated user.

        Args:
            request: Current HTTP request.
            tenant_id: Tenant identifier requested by the user.

        Returns:
            HttpResponse: Redirect response to the requested ``next`` location or the owner admin.
        """
        ActiveTenantSwitcher.switch(request, tenant_id)

        next_url = request.GET.get("next", "")
        if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            logger.info(
                "Redirected tenant switch to safe next url tenant_id=%s next_url=%r",
                tenant_id,
                next_url,
            )
            return redirect(next_url)

        logger.info(
            "Redirected tenant switch to owner admin index because next url was missing or unsafe tenant_id=%s",
            tenant_id,
        )
        return redirect(reverse("owner_admin:index"))
