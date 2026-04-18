""" Future path-based strategy for active-tenant resolution. """

from django.http import HttpRequest
from tenancy.models import TenantModel
from tenancy.resolution.strategies.tenant_resolution_strategy import TenantResolutionStrategy


class PathTenantResolutionStrategy(TenantResolutionStrategy):
    """ Reserve one explicit strategy slot for future path-based tenant resolution.

    The current project runtime does not resolve the active tenant from the URL path yet.
    This strategy intentionally returns ``None`` until a tenant-aware frontend path contract
    is introduced and documented.
    """

    @classmethod
    def resolve(cls, request: HttpRequest) -> TenantModel | None:
        """ Return ``None`` until path-based tenant resolution is activated.

        Args:
            request: Current HTTP request.

        Returns:
            TenantModel | None: Always ``None`` in the current runtime.
        """
        return None
