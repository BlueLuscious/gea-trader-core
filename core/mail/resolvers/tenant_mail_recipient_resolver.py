""" Tenant-aware helpers for resolving business contact recipients. """

from typing import TYPE_CHECKING
from core.mail.dtos import MailRecipientDTO
from core.mail.resolvers.tenant_mail_context_resolver import TenantMailContextResolver

if TYPE_CHECKING:
    from tenancy.models import TenantModel


class TenantMailRecipientResolver:
    """ Resolve the preferred tenant contact recipient for outbound business mail. """

    context_resolver_class = TenantMailContextResolver

    @classmethod
    def resolve_contact_email(cls, tenant: "TenantModel | None") -> str | None:
        """ Return the preferred tenant-facing contact email.

        Args:
            tenant: Tenant whose business contact channel should be used.

        Returns:
            str | None: Preferred support email, business email fallback, or ``None``.
        """
        return cls.context_resolver_class.get_support_email(tenant)

    @classmethod
    def resolve_contact_recipient(cls, tenant: "TenantModel | None") -> MailRecipientDTO | None:
        """ Return the preferred tenant-facing recipient object.

        Args:
            tenant: Tenant whose business contact recipient should be used.

        Returns:
            MailRecipientDTO | None: Tenant-facing recipient built from the preferred contact email.
        """
        contact_email = cls.resolve_contact_email(tenant)
        if not contact_email:
            return None

        display_name = cls.context_resolver_class.get_product_name(
            tenant,
            cls.context_resolver_class.get_branding(tenant),
        )
        return MailRecipientDTO(email=contact_email, name=display_name)
