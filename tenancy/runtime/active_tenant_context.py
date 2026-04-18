""" Runtime context helpers for the active tenant. """

from contextvars import ContextVar, Token
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tenancy.models import TenantModel


_CURRENT_TENANT: ContextVar["TenantModel | None"] = ContextVar("current_tenant", default=None)


class ActiveTenantContext:
    """ Manage the active tenant bound to the current execution context. """

    @classmethod
    def set(cls, tenant: "TenantModel | None") -> Token["TenantModel | None"]:
        """ Store the active tenant in the current execution context.

        Args:
            tenant: Tenant that should be available during the active request flow.

        Returns:
            Token[TenantModel | None]: Context token used to restore the previous value.
        """
        return _CURRENT_TENANT.set(tenant)

    @classmethod
    def reset(cls, token: Token["TenantModel | None"]) -> None:
        """ Restore the previous tenant value for the current execution context.

        Args:
            token: Context token returned by :meth:`set`.
        """
        _CURRENT_TENANT.reset(token)

    @classmethod
    def get(cls) -> "TenantModel | None":
        """ Return the active tenant stored in the current execution context.

        Returns:
            TenantModel | None: Active tenant for the current request flow, when present.
        """
        return _CURRENT_TENANT.get()
