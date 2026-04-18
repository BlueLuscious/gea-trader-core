""" Service for resolving the active tenant for one request. """

from django.http import HttpRequest
from tenancy.models import TenantModel
from tenancy.resolution.admin_active_tenant_resolver import AdminActiveTenantResolver


class ActiveTenantResolver:
    """ Resolve the active tenant for one request using the current admin strategy set. """

    resolver_class = AdminActiveTenantResolver

    @classmethod
    def resolve(cls, request: HttpRequest) -> TenantModel | None:
        """ Resolve the active tenant for the current request.

        Args:
            request: Current HTTP request.

        Returns:
            TenantModel | None: Resolved active tenant or ``None``.
        """
        return cls.resolver_class.resolve(request)
