""" Session-backed strategy for active-tenant resolution. """

import logging
from django.http import HttpRequest
from tenancy.models import TenantMembershipModel, TenantModel
from tenancy.resolution.strategies.tenant_resolution_strategy import TenantResolutionStrategy
from tenancy.session import ActiveTenantSessionStore

logger = logging.getLogger(__name__)


class SessionTenantResolutionStrategy(TenantResolutionStrategy):
    """ Resolve the active tenant from session when the membership is still valid. """

    session_store_class = ActiveTenantSessionStore
    membership_model = TenantMembershipModel

    @classmethod
    def resolve(cls, request: HttpRequest) -> TenantModel | None:
        """ Return the session-selected tenant when the user still belongs to it.

        Args:
            request: Current HTTP request.

        Returns:
            TenantModel | None: Session-selected tenant or ``None``.
        """
        session_tenant_id = cls.session_store_class.get_tenant_id(request)
        if not session_tenant_id:
            return None

        membership = (
            cls.membership_model.objects.for_user_active_tenants(request.user)
            .with_tenant()
            .filter(tenant_id=session_tenant_id)
            .first()
        )

        if membership is None:
            cls.session_store_class.clear(request)
            logger.info(
                "Cleared stale active tenant session selection tenant_id=%s",
                session_tenant_id,
            )
            return None

        logger.info(
            "Resolved active tenant from session tenant_id=%s",
            membership.tenant.pk,
        )
        return membership.tenant
