""" Active-tenant resolver used by the current admin runtime. """

import logging
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from tenancy.models import TenantModel
from tenancy.resolution.composite_tenant_resolver import CompositeTenantResolver
from tenancy.resolution.strategies.membership_tenant_resolution_strategy import MembershipTenantResolutionStrategy
from tenancy.resolution.strategies.session_tenant_resolution_strategy import SessionTenantResolutionStrategy
from tenancy.session import ActiveTenantSessionStore

logger = logging.getLogger(__name__)


class AdminActiveTenantResolver(CompositeTenantResolver):
    """ Resolve the active tenant for the current admin flow.

    Resolution order:
    1. Active tenant stored in session, when the user still belongs to it.
    2. Primary active tenant membership for the authenticated user.
    3. First active tenant membership for the authenticated user.
    """

    session_store_class = ActiveTenantSessionStore
    strategies = (
        SessionTenantResolutionStrategy,
        MembershipTenantResolutionStrategy,
    )

    @classmethod
    def resolve(cls, request: HttpRequest) -> TenantModel | None:
        """ Resolve the active tenant for the current admin request.

        Args:
            request: Current HTTP request.

        Returns:
            TenantModel | None: Resolved tenant or ``None``.
        """
        user = request.user

        if isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
            cls.session_store_class.clear(request)
            logger.info("Cleared active tenant session state for an anonymous-like request")
            return None

        return super().resolve(request)
