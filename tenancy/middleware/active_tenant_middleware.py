""" Middleware for request-time active tenant resolution. """

from collections.abc import Callable
import logging
from django.http import HttpRequest, HttpResponse
from tenancy.runtime import ActiveTenantContext
from tenancy.resolution.active_tenant_resolver import ActiveTenantResolver

logger = logging.getLogger(__name__)


class ActiveTenantMiddleware:
    """ Attach the active tenant to each request after authentication. """

    resolver_class = ActiveTenantResolver
    context_class = ActiveTenantContext

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """ Store the next middleware or view callable.

        Args:
            get_response: Next middleware or view callable.
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """ Resolve and attach the active tenant before continuing the request.

        Args:
            request: Current HTTP request.

        Returns:
            HttpResponse: Response produced by the remaining stack.
        """
        request.tenant = self.resolver_class.resolve(request)
        logger.info(
            "Attached active tenant to request path=%r tenant_id=%s",
            request.path,
            getattr(request.tenant, "pk", None),
        )
        tenant_token = self.context_class.set(request.tenant)

        try:
            return self.get_response(request)
        finally:
            self.context_class.reset(tenant_token)
