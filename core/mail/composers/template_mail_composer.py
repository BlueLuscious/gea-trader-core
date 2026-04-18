""" Compose templated outbound mail into transport-ready DTOs. """

from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterator
from core.mail.dtos import MailMessageDTO, TemplateMailRequestDTO
from core.mail.factories import TemplateMailMessageFactory
from core.mail.policies import SystemMailSenderPolicy
from tenancy.runtime import ActiveTenantContext

if TYPE_CHECKING:
    from tenancy.models import TenantModel


class TemplateMailComposer:
    """ Compose one templated outbound mail request into one mail message DTO. """

    message_factory_class = TemplateMailMessageFactory
    tenant_context_class = ActiveTenantContext
    sender_policy_class = SystemMailSenderPolicy

    @classmethod
    def compose(cls, request: TemplateMailRequestDTO) -> MailMessageDTO:
        """ Compose one templated mail request into one transport-ready payload.

        Args:
            request: Templated outbound mail request.

        Returns:
            MailMessageDTO: Outbound mail payload ready for delivery.
        """
        resolved_from_email = cls.sender_policy_class.resolve(
            explicit_from_email=request.from_email,
            tenant=request.tenant,
        )

        with cls._use_tenant_context(request.tenant):
            return cls.message_factory_class.build(
                request=request,
                from_email=resolved_from_email,
            )

    @classmethod
    @contextmanager
    def _use_tenant_context(cls, tenant: "TenantModel | None") -> Iterator[None]:
        """ Temporarily bind one explicit tenant to the current mail composition flow.

        Args:
            tenant: Tenant to bind while the mail payload is composed.

        Yields:
            Iterator[None]: Empty context manager body.
        """
        if tenant is None:
            yield
            return

        tenant_token = cls.tenant_context_class.set(tenant)

        try:
            yield
        finally:
            cls.tenant_context_class.reset(tenant_token)
