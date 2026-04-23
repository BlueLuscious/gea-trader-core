""" Tenant-aware base context helpers for outbound mail templates. """

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin
from django.core.exceptions import ObjectDoesNotExist
from tenancy.runtime import ActiveTenantContext

if TYPE_CHECKING:
    from tenancy.models import TenantBrandingModel, TenantModel


class TenantMailContextResolver:
    """ Resolve tenant-aware base context values for outbound mail templates. """

    context_class = ActiveTenantContext

    @classmethod
    def resolve(cls) -> dict[str, Any]:
        """ Build one tenant-aware base context for mail rendering.

        Returns:
            dict[str, Any]: Mail base context derived from the active tenant when one exists.
        """
        tenant = cls.context_class.get()
        branding = cls.get_branding(tenant)

        return {
            "product_name": cls.get_product_name(tenant, branding),
            "product_logo_url": cls.get_product_logo_url(tenant, branding),
            "support_email": cls.get_support_email(tenant),
            "phone_number": cls.get_phone_number(tenant),
            "website_url": cls.get_website_url(tenant),
        }

    @staticmethod
    def get_branding(tenant: "TenantModel | None") -> "TenantBrandingModel | None":
        """ Return branding for one tenant when it is available.

        Args:
            tenant: Active tenant bound to the current runtime context.

        Returns:
            TenantBrandingModel | None: Related branding row or ``None``.
        """
        if tenant is None:
            return None

        cached_branding: "TenantBrandingModel | None" = tenant._state.fields_cache.get("branding")
        if cached_branding is not None:
            return cached_branding

        if getattr(tenant._state, "adding", False):
            return None

        try:
            return getattr(tenant, "branding", None)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_product_name(
        tenant: "TenantModel | None",
        branding: "TenantBrandingModel | None",
    ) -> str | None:
        """ Return the preferred product or business name for one mail context.

        Args:
            tenant: Active tenant bound to the current runtime context.
            branding: Optional branding row for the active tenant.

        Returns:
            str | None: Preferred display name or ``None``.
        """
        display_name = str(getattr(branding, "display_name", "") or "").strip()
        if display_name:
            return display_name

        tenant_name = str(getattr(tenant, "name", "") or "").strip()
        if tenant_name:
            return tenant_name

        return None

    @classmethod
    def get_product_logo_url(
        cls,
        tenant: "TenantModel | None",
        branding: "TenantBrandingModel | None",
    ) -> str | None:
        """ Return the preferred logo URL for one mail context.

        Args:
            cls: Resolver class.
            tenant: Active tenant bound to the current runtime context.
            branding: Optional branding row for the active tenant.

        Returns:
            str | None: Preferred logo URL or ``None``.
        """
        if branding is None:
            return None

        for field_name in ("logo_light", "logo_dark", "icon_light", "icon_dark"):
            asset = getattr(branding, field_name, None)
            if asset:
                return cls.build_public_asset_url(tenant, asset.url)

        return None

    @classmethod
    def build_public_asset_url(cls, tenant: "TenantModel | None", asset_url: str) -> str:
        """ Return one public absolute asset URL when a tenant website exists.

        Args:
            tenant: Active tenant bound to the current runtime context.
            asset_url: Raw asset URL exposed by the storage backend.

        Returns:
            str: Absolute asset URL when possible, otherwise the original value.
        """
        normalized_asset_url = str(asset_url or "").strip()
        if not normalized_asset_url:
            return ""

        if normalized_asset_url.startswith(("http://", "https://")):
            return normalized_asset_url

        website_url = cls.get_website_url(tenant)
        if not website_url:
            return normalized_asset_url

        return urljoin(f"{website_url.rstrip('/')}/", normalized_asset_url.lstrip("/"))

    @staticmethod
    def get_support_email(tenant: "TenantModel | None") -> str | None:
        """ Return the preferred support email for one mail context.

        Args:
            tenant: Active tenant bound to the current runtime context.

        Returns:
            str | None: Support email, business email fallback, or ``None``.
        """
        support_email = str(getattr(tenant, "support_email", "") or "").strip()
        if support_email:
            return support_email

        business_email = str(getattr(tenant, "business_email", "") or "").strip()
        if business_email:
            return business_email

        return None

    @staticmethod
    def get_phone_number(tenant: "TenantModel | None") -> str | None:
        """ Return the phone number for one mail context when present.

        Args:
            tenant: Active tenant bound to the current runtime context.

        Returns:
            str | None: Public phone number or ``None``.
        """
        phone_number = str(getattr(tenant, "phone_number", "") or "").strip()
        return phone_number or None

    @staticmethod
    def get_website_url(tenant: "TenantModel | None") -> str | None:
        """ Return the website URL for one mail context when present.

        Args:
            tenant: Active tenant bound to the current runtime context.

        Returns:
            str | None: Public website URL or ``None``.
        """
        website_url = str(getattr(tenant, "website_url", "") or "").strip()
        return website_url or None
