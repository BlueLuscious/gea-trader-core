""" Membership-backed fallback strategy for active-tenant resolution. """

import logging
from django.http import HttpRequest
from tenancy.models import TenantMembershipModel, TenantModel
from tenancy.resolution.strategies.tenant_resolution_strategy import TenantResolutionStrategy
from tenancy.session import ActiveTenantSessionStore

logger = logging.getLogger(__name__)


class MembershipTenantResolutionStrategy(TenantResolutionStrategy):
    """ Resolve the active tenant from the user's active memberships. """

    membership_model = TenantMembershipModel
    session_store_class = ActiveTenantSessionStore

    @classmethod
    def resolve(cls, request: HttpRequest) -> TenantModel | None:
        """ Return the primary or first active tenant membership for the user.

        Args:
            request: Current HTTP request.

        Returns:
            TenantModel | None: Fallback tenant resolved from memberships.
        """
        membership = (
            cls.membership_model.objects.for_user_active_tenants(request.user)
            .with_tenant()
            .ordered_for_active_tenant_resolution()
            .first()
        )

        if membership is None:
            cls.session_store_class.clear(request)
            logger.info("No active tenant membership fallback was available for the current user")
            return None

        cls.session_store_class.set_tenant(request, membership.tenant)
        logger.info(
            "Resolved active tenant from membership fallback tenant_id=%s is_primary=%s",
            membership.tenant.pk,
            membership.is_primary,
        )
        return membership.tenant
