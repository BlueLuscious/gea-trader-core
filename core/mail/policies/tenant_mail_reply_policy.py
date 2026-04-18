""" Policy helpers for deciding reply-to behavior in tenant-aware mail flows. """

from typing import TYPE_CHECKING
from core.mail.resolvers import TenantMailRecipientResolver

if TYPE_CHECKING:
    from tenancy.models import TenantModel


class TenantMailReplyPolicy:
    """ Decide reply-to addresses for tenant-aware outbound mail flows. """

    recipient_resolver_class = TenantMailRecipientResolver

    @staticmethod
    def _normalize_email(email: str | None) -> str | None:
        """ Normalize one optional email address.

        Args:
            email: Optional email address.

        Returns:
            str | None: Stripped email address or ``None``.
        """
        normalized_email = str(email or "").strip()
        return normalized_email or None

    @classmethod
    def resolve_customer_reply_to(cls, customer_email: str | None) -> tuple[str, ...]:
        """ Return the reply-to target for one customer-originated request.

        Args:
            customer_email: Customer email address that should receive owner replies.

        Returns:
            tuple[str, ...]: Reply-to addresses for the outbound message.
        """
        normalized_email = cls._normalize_email(customer_email)
        return (normalized_email,) if normalized_email else ()

    @classmethod
    def resolve_tenant_contact_reply_to(cls, tenant: "TenantModel | None") -> tuple[str, ...]:
        """ Return the reply-to target for one tenant-facing business reply channel.

        Args:
            tenant: Tenant whose preferred contact email should receive replies.

        Returns:
            tuple[str, ...]: Reply-to addresses for the outbound message.
        """
        contact_email = cls.recipient_resolver_class.resolve_contact_email(tenant)
        return (contact_email,) if contact_email else ()
