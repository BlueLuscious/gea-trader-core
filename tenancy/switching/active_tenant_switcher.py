""" Service for explicit active-tenant switching. """

from uuid import UUID
import logging
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from tenancy.models import TenantMembershipModel
from tenancy.session import ActiveTenantSessionStore

logger = logging.getLogger(__name__)


class ActiveTenantSwitcher:
    """ Switch the active tenant for one request after validating membership access. """

    session_store_class = ActiveTenantSessionStore

    @classmethod
    def switch(cls, request: HttpRequest, tenant_id: UUID) -> None:
        """ Switch the active tenant for the current authenticated user.

        Args:
            request: Current HTTP request.
            tenant_id: Tenant identifier requested by the user.

        Raises:
            PermissionDenied: If the user does not belong to the requested tenant.
        """
        membership = (
            TenantMembershipModel.objects.for_user_active_tenants(request.user)
            .with_tenant()
            .filter(tenant_id=tenant_id)
            .first()
        )

        if membership is None:
            logger.warning(
                "Rejected active tenant switch user_id=%s tenant_id=%s because no active membership matched",
                getattr(request.user, "pk", None),
                tenant_id,
            )
            raise PermissionDenied(_("You do not have access to the requested business."))

        cls.session_store_class.set_tenant(request, membership.tenant)
        logger.info(
            "Switched active tenant user_id=%s tenant_id=%s",
            getattr(request.user, "pk", None),
            membership.tenant.pk,
        )
