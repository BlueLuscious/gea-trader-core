""" Composite active-tenant resolver built from small strategies. """

import logging
from typing import TYPE_CHECKING
from django.http import HttpRequest
from tenancy.models import TenantModel

if TYPE_CHECKING:
    from tenancy.resolution.strategies.tenant_resolution_strategy import TenantResolutionStrategy

logger = logging.getLogger(__name__)


class CompositeTenantResolver:
    """ Resolve one tenant by trying small strategies in order. """

    strategies: tuple[type["TenantResolutionStrategy"], ...] = ()

    @classmethod
    def resolve(cls, request: HttpRequest) -> TenantModel | None:
        """ Return the first tenant resolved by the configured strategies.

        Args:
            request: Current HTTP request.

        Returns:
            TenantModel | None: First resolved tenant or ``None`` when no strategy matches.
        """
        for strategy_class in cls.strategies:
            tenant = strategy_class.resolve(request)
            if tenant is not None:
                logger.info(
                    "Resolved active tenant strategy=%s tenant_id=%s",
                    strategy_class.__name__,
                    tenant.pk,
                )
                return tenant

        logger.info("No active tenant strategy matched for the current request")
        return None
