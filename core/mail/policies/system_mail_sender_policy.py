""" Policy helpers for deciding the effective system mail sender. """

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tenancy.models import TenantModel


class SystemMailSenderPolicy:
    """ Decide the effective technical sender for outbound mail. """

    @staticmethod
    def resolve(
        *,
        explicit_from_email: str | None = None,
        tenant: "TenantModel | None" = None,
    ) -> str | None:
        """ Return the explicit sender override when present.

        Args:
            explicit_from_email: Optional sender override provided by the caller.
            tenant: Optional tenant for future sender-policy expansion.

        Returns:
            str | None: Explicit sender override or ``None`` so Django falls back to `DEFAULT_FROM_EMAIL`.
        """
        del tenant

        normalized_from_email = str(explicit_from_email or "").strip()
        return normalized_from_email or None
