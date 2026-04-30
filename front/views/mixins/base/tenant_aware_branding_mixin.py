""" Tenant-aware branding helpers for public storefront views. """

import re
from tenancy.models import TenantBrandingModel, TenantModel


class TenantAwareBrandingMixin:
    """ Build tenant-aware branding and contact context for storefront views. """

    tenant_context_name = "current_tenant"

    @staticmethod
    def build_whatsapp_url(phone_number: str) -> str:
        """ Build a WhatsApp deep link from a public phone number.

        Args:
            phone_number: Tenant public phone number.

        Returns:
            str: WhatsApp deep link or an empty string when no valid digits exist.
        """
        normalized_phone = re.sub(r"\D+", "", phone_number)
        if not normalized_phone:
            return ""

        return f"https://wa.me/{normalized_phone}"

    @staticmethod
    def get_brand_name(tenant: TenantModel) -> str:
        """ Return the public display name for the site tenant.

        Args:
            tenant: Active public tenant.

        Returns:
            str: Branding display name or fallback tenant name.
        """
        branding: TenantBrandingModel = getattr(tenant, "branding", None)
        if branding is not None and branding.display_name:
            return branding.display_name

        return tenant.name

    @staticmethod
    def get_contact_email(tenant: TenantModel) -> str:
        """ Return the best public contact email for the current tenant.

        Args:
            tenant: Active public tenant.

        Returns:
            str: Business email first, then support email, or an empty string.
        """
        return tenant.business_email or tenant.support_email or ""

    def build_social_links(self, branding: TenantBrandingModel | None) -> list[dict[str, str]]:
        """ Build storefront social-link payloads from tenant branding.

        Args:
            branding: Tenant branding record when one exists.

        Returns:
            list[dict[str, str]]: Ordered social-link payloads ready for template rendering.
        """
        if branding is None:
            return []

        social_candidates: tuple[tuple[str, str, str], ...] = (
            ("Instagram", "instagram", branding.instagram_url),
            ("Facebook", "facebook-f", branding.facebook_url),
            ("LinkedIn", "linkedin-in", branding.linkedin_url),
        )
        return [
            {"label": label, "icon": icon, "url": url}
            for label, icon, url in social_candidates
            if url
        ]

    def build_tenant_branding_context(self, tenant: TenantModel) -> dict[str, object]:
        """ Build tenant-aware branding and contact context for the public site.

        Args:
            tenant: Active public tenant.

        Returns:
            dict[str, object]: Branding and contact context for public templates.
        """
        branding: TenantBrandingModel = getattr(tenant, "branding", None)
        logo_light_url = (
            branding.logo_light.url
            if branding is not None and getattr(branding, "logo_light", None)
            else None
        )
        logo_dark_url = (
            branding.logo_dark.url
            if branding is not None and getattr(branding, "logo_dark", None)
            else logo_light_url
        )
        favicon_light_url = (
            branding.favicon_light.url
            if branding is not None and getattr(branding, "favicon_light", None)
            else None
        )
        favicon_dark_url = (
            branding.favicon_dark.url
            if branding is not None and getattr(branding, "favicon_dark", None)
            else favicon_light_url
        )
        contact_email = self.get_contact_email(tenant)
        return {
            self.tenant_context_name: tenant,
            "site_brand_name": self.get_brand_name(tenant),
            "site_logo_light_url": logo_light_url,
            "site_logo_dark_url": logo_dark_url,
            "site_favicon_light_url": favicon_light_url,
            "site_favicon_dark_url": favicon_dark_url,
            "site_contact_email": contact_email,
            "site_phone_number": tenant.phone_number,
            "site_whatsapp_url": self.build_whatsapp_url(tenant.phone_number),
            "site_social_links": self.build_social_links(branding),
        }
