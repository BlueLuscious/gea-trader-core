""" Middleware for request-time active tenant resolution. """

import logging
from collections.abc import Callable
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from tenancy.runtime import ActiveTenantContext
from tenancy.resolution.active_tenant_resolver import ActiveTenantResolver

logger = logging.getLogger(__name__)


class ActiveTenantMiddleware:
    """ Attach the active tenant to each request after authentication. """

    resolver_class = ActiveTenantResolver
    context_class = ActiveTenantContext
    tenant_aware_path_prefixes = ("/owner-admin/",)

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
        if self.should_resolve_request(request):
            request.tenant = self.resolver_class.resolve(request)
            logger.info(
                "Attached active tenant to request path=%r tenant_id=%s",
                request.path,
                getattr(request.tenant, "pk", None),
            )
        else:
            request.tenant = None
            logger.debug("Skipped active tenant resolution for path=%r", request.path)

        tenant_token = self.context_class.set(request.tenant)

        try:
            return self.get_response(request)
        finally:
            self.context_class.reset(tenant_token)

    @classmethod
    def should_resolve_request(cls, request: HttpRequest) -> bool:
        """ Return whether the current request belongs to a tenant-aware surface.

        Args:
            request: Current HTTP request.

        Returns:
            bool: ``True`` when active-tenant resolution should run.
        """
        path = request.path if request.path.startswith("/") else f"/{request.path}"
        return any(cls._path_matches_prefix(path, prefix) for prefix in cls._localized_prefixes())

    @classmethod
    def _localized_prefixes(cls) -> tuple[str, ...]:
        """ Return tenant-aware prefixes with optional language variants.

        Returns:
            tuple[str, ...]: Supported path prefixes for active-tenant resolution.
        """
        prefixes = list(cls.tenant_aware_path_prefixes)
        for language_code, _language_name in settings.LANGUAGES:
            language_prefix = f"/{language_code}"
            prefixes.extend(f"{language_prefix}{prefix}" for prefix in cls.tenant_aware_path_prefixes)
        return tuple(prefixes)

    @staticmethod
    def _path_matches_prefix(path: str, prefix: str) -> bool:
        """ Return whether one request path is inside one configured prefix.

        Args:
            path: Request path.
            prefix: Tenant-aware prefix.

        Returns:
            bool: ``True`` when the path matches the prefix or its slashless form.
        """
        slashless_prefix = prefix.rstrip("/")
        return path == slashless_prefix or path.startswith(prefix)
