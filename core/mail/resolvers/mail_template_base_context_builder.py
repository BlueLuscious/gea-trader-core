""" Build the effective base context used by outbound mail templates. """

from contextlib import contextmanager
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Iterator
from core.mail.resolvers.tenant_mail_context_resolver import TenantMailContextResolver
from tenancy.runtime import ActiveTenantContext

if TYPE_CHECKING:
    from tenancy.models import TenantModel


class MailTemplateBaseContextBuilder:
    """ Build one outbound mail template context from tenant-aware defaults and caller overrides. """

    tenant_context_resolver_class = TenantMailContextResolver
    tenant_context_class = ActiveTenantContext

    @classmethod
    def build(cls, context: Mapping[str, Any], tenant: "TenantModel | None" = None) -> dict[str, Any]:
        """ Build one effective mail template context.

        Args:
            context: Caller-supplied context values.
            tenant: Optional explicit tenant used to snapshot tenant-aware defaults.

        Returns:
            dict[str, Any]: Effective template context with caller values taking precedence.
        """
        with cls._use_tenant_context(tenant):
            return {
                **cls.tenant_context_resolver_class.resolve(),
                **dict(context),
            }

    @classmethod
    @contextmanager
    def _use_tenant_context(cls, tenant: "TenantModel | None") -> Iterator[None]:
        """ Temporarily bind one explicit tenant while one mail context is built.

        Args:
            tenant: Optional explicit tenant instance.

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
