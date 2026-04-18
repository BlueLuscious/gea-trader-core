""" Helpers for tenant-aware media object paths. """

from tenancy.runtime import ActiveTenantContext


class TenantMediaPathBuilder:
    """ Build tenant-aware media paths from the current runtime tenant context. """

    context_class = ActiveTenantContext

    @classmethod
    def build_current_tenant_media_prefix(cls) -> str | None:
        """ Build the media prefix for the active tenant, when one exists.

        Returns:
            str | None: Tenant-specific media prefix or ``None`` when no tenant is active.
        """
        tenant = cls.context_class.get()
        if tenant is None:
            return None

        tenant_key = tenant.slug.strip()
        return f"tenants/{tenant_key}"

    @classmethod
    def build_tenant_media_name(cls, name: str) -> str:
        """ Build one tenant-aware media object name.

        Args:
            name: Relative media object name produced by the caller.

        Returns:
            str: Tenant-aware media object name.
        """
        normalized_name = name.lstrip("/")
        tenant_prefix = cls.build_current_tenant_media_prefix()

        if tenant_prefix is None or normalized_name.startswith(f"{tenant_prefix}/"):
            return normalized_name

        return f"{tenant_prefix}/{normalized_name}"
