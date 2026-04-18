""" Tenant-branding resolver used by the owner admin site. """

import logging
from typing import TYPE_CHECKING
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest

if TYPE_CHECKING:
    from django.db.models.fields.files import ImageFieldFile
    from tenancy.models import TenantBrandingModel, TenantModel

logger = logging.getLogger(__name__)


class OwnerTenantBrandingResolver:
    """ Resolve tenant branding assets for the owner admin site. """

    @classmethod
    def get_branding(cls, request: HttpRequest) -> "TenantBrandingModel | None":
        """ Return tenant branding for the current request when available.

        Args:
            request: Current admin request.

        Returns:
            TenantBrandingModel | None: Tenant branding object or ``None``.
        """
        tenant: "TenantModel | None" = getattr(request, "tenant", None)
        if tenant is None:
            logger.info("Skipped owner tenant branding resolution because no active tenant is bound to the request")
            return None

        cached_branding: "TenantBrandingModel | None" = tenant._state.fields_cache.get("branding")
        if cached_branding is not None:
            return cached_branding

        if getattr(tenant._state, "adding", False):
            logger.info("Skipped owner tenant branding resolution because the active tenant is not persisted yet")
            return None

        try:
            return getattr(tenant, "branding", None)
        except ObjectDoesNotExist:
            logger.info("Owner tenant branding was not configured for tenant_id=%s", tenant.pk)
            return None

    @classmethod
    def get_display_name(cls, request: HttpRequest) -> str | None:
        """ Return the preferred tenant display name for owner admin branding.

        Args:
            request: Current admin request.

        Returns:
            str | None: Branding display name, tenant name fallback, or ``None``.
        """
        branding = cls.get_branding(request)
        display_name: str = getattr(branding, "display_name", "")
        if display_name:
            return str(display_name)

        tenant: "TenantModel | None" = getattr(request, "tenant", None)
        tenant_name: str = getattr(tenant, "name", "")
        if tenant_name:
            return str(tenant_name)

        return None

    @staticmethod
    def get_file_url(field: "ImageFieldFile") -> str | None:
        """ Return the URL of one file-like field when available.

        Args:
            field: File-like object or ``None``.

        Returns:
            str | None: File URL when the field is populated.
        """
        if not field:
            return None

        return getattr(field, "url", None)

    @classmethod
    def build_themed_asset(cls, light_field: "ImageFieldFile", dark_field: "ImageFieldFile") -> dict[str, str] | str | None:
        """ Build the Unfold asset payload for one optional light or dark pair.

        Args:
            light_field: Light-themed file-like field.
            dark_field: Dark-themed file-like field.

        Returns:
            dict[str, str] | str | None: Theme-aware asset mapping, single URL, or ``None``.
        """
        light_url = cls.get_file_url(light_field)
        dark_url = cls.get_file_url(dark_field)

        if light_url and dark_url:
            return {
                "light": light_url,
                "dark": dark_url,
            }

        return light_url or dark_url

    @staticmethod
    def build_favicon_entry(href: str) -> dict[str, str]:
        """ Build one favicon entry for Unfold.

        Args:
            href: Public URL of the favicon asset.

        Returns:
            dict[str, str]: Normalized favicon metadata.
        """
        return {
            "href": href,
            "rel": "icon",
            "type": "image/png",
        }

    @classmethod
    def get_logo(cls, request: HttpRequest) -> dict[str, str] | str | None:
        """ Return the owner-site logo payload from tenant branding.

        Args:
            request: Current admin request.

        Returns:
            dict[str, str] | str | None: Unfold-compatible logo payload.
        """
        branding = cls.get_branding(request)
        return cls.build_themed_asset(
            getattr(branding, "logo_light", None),
            getattr(branding, "logo_dark", None),
        )

    @classmethod
    def get_icon(cls, request: HttpRequest) -> dict[str, str] | str | None:
        """ Return the owner-site icon payload from tenant branding.

        Args:
            request: Current admin request.

        Returns:
            dict[str, str] | str | None: Unfold-compatible icon payload.
        """
        branding = cls.get_branding(request)
        return cls.build_themed_asset(
            getattr(branding, "icon_light", None),
            getattr(branding, "icon_dark", None),
        )

    @classmethod
    def get_favicons(cls, request: HttpRequest) -> list[dict[str, str]]:
        """ Return the owner-site favicon entries from tenant branding.

        Args:
            request: Current admin request.

        Returns:
            list[dict[str, str]]: Favicon metadata consumed by Unfold.
        """
        branding = cls.get_branding(request)
        light_url = cls.get_file_url(getattr(branding, "favicon_light", None))
        dark_url = cls.get_file_url(getattr(branding, "favicon_dark", None))
        favicons: list[dict[str, str]] = []

        if light_url:
            favicons.append(cls.build_favicon_entry(light_url))

        if dark_url:
            favicons.append(cls.build_favicon_entry(dark_url))

        return favicons
