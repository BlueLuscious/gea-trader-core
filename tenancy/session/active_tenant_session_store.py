""" Session helpers for the active tenant. """

from typing import TYPE_CHECKING
from django.http import HttpRequest
from tenancy.constants import ACTIVE_TENANT_SESSION_KEY

if TYPE_CHECKING:
    from tenancy.models import TenantModel


class ActiveTenantSessionStore:
    """ Encapsulate session-backed persistence for the active tenant. """

    session_key = ACTIVE_TENANT_SESSION_KEY

    @classmethod
    def get_tenant_id(cls, request: HttpRequest) -> str | None:
        """ Return the active tenant identifier stored in session.

        Args:
            request: Current HTTP request.

        Returns:
            str | None: Stored tenant identifier when present.
        """
        return request.session.get(cls.session_key)

    @classmethod
    def set_tenant(cls, request: HttpRequest, tenant: "TenantModel") -> None:
        """ Store one tenant as the active tenant for the current session.

        Args:
            request: Current HTTP request.
            tenant: Tenant that should become active for the session.
        """
        request.session[cls.session_key] = str(tenant.pk)

    @classmethod
    def clear(cls, request: HttpRequest) -> None:
        """ Remove the active tenant marker from the current session.

        Args:
            request: Current HTTP request.
        """
        request.session.pop(cls.session_key, None)
