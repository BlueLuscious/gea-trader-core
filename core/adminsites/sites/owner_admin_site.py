""" Owner admin site definition. """

from typing import Any, TYPE_CHECKING
from django.http import HttpRequest
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _
from core.adminsites.services import OwnerTenantDropdownBuilder
from core.adminsites.services import OwnerTenantBrandingResolver
from core.adminsites.services import OwnerTenantSidebarNavigationBuilder
from core.adminsites.sites.base_admin_site import BaseAdminSite

if TYPE_CHECKING:
    from tenancy.models.tenant_membership_model import TenantMembershipModel, TenantModel


class OwnerAdminSite(BaseAdminSite):
    """ Guided admin site intended for business owners and operators. """

    settings_name = "OWNER_ADMIN_UNFOLD"
    site_header = _("Business Administration")
    site_title = _("Business Admin")
    site_symbol = "storefront"
    index_title = _("Business operations")

    @classmethod
    def get_site_title(cls, request: HttpRequest) -> str:
        """ Return the owner site title, preferring the active tenant name.

        Args:
            request: Current admin request.

        Returns:
            str: Tenant-aware site title.
        """
        display_name = OwnerTenantBrandingResolver.get_display_name(request)
        if display_name:
            return display_name

        return super().get_site_title(request)

    @classmethod
    def get_site_header(cls, request: HttpRequest) -> str:
        """ Return the owner site header, preferring the active tenant name.

        Args:
            request: Current admin request.

        Returns:
            str: Tenant-aware site header.
        """
        display_name = OwnerTenantBrandingResolver.get_display_name(request)
        if display_name:
            return display_name

        return super().get_site_header(request)

    @classmethod
    def get_site_logo(cls, request: HttpRequest) -> dict[str, str] | str | None:
        """ Return the owner site logo from tenant branding when available.

        Args:
            request: Current admin request.

        Returns:
            dict[str, str] | str | None: Tenant-aware logo payload.
        """
        return OwnerTenantBrandingResolver.get_logo(request)

    @classmethod
    def get_site_icon(cls, request: HttpRequest) -> dict[str, str] | str | None:
        """ Return the owner site icon from tenant branding when available.

        Args:
            request: Current admin request.

        Returns:
            dict[str, str] | str | None: Tenant-aware icon payload.
        """
        return OwnerTenantBrandingResolver.get_icon(request)

    @classmethod
    def get_site_favicons(cls, request: HttpRequest) -> list[dict[str, str]]:
        """ Return tenant-specific favicon entries when branding provides them.

        Args:
            request: Current admin request.

        Returns:
            list[dict[str, str]]: Favicon metadata for Unfold.
        """
        return OwnerTenantBrandingResolver.get_favicons(request)

    @classmethod
    def get_environment(cls, request: HttpRequest) -> list[str] | None:
        """ Return the owner environment badge using the active membership role.

        Args:
            request: Current admin request.

        Returns:
            list[str] | None: Role label and badge variant, or ``None`` when unavailable.
        """
        tenant: "TenantModel | None" = getattr(request, "tenant", None)
        tenant_id: str = getattr(tenant, "pk", None)

        if tenant_id is None:
            return None

        membership: "TenantMembershipModel | None" = request.user.tenant_memberships.filter(
            tenant_id=tenant_id,
            is_active=True,
        ).first()

        if membership is None:
            return None

        return [membership.get_role_display(), "primary"]

    def has_permission(self, request: HttpRequest) -> bool:
        """ Return whether the request user can access the owner admin site.

        Args:
            request: Current admin request.

        Returns:
            bool: True when the request user is an active staff user.
        """
        user = request.user
        return bool(user.is_active and user.is_staff)

    def get_site_dropdown(self, request: HttpRequest) -> list[dict[str, Any]]:
        """ Return tenant switcher items for the current owner admin request.

        Args:
            request: Current admin request.

        Returns:
            list[dict[str, Any]]: Dropdown items for active tenant memberships.
        """
        return OwnerTenantDropdownBuilder.build(request)

    def get_sidebar_navigation(self, request: HttpRequest) -> list[dict[str, Any]]:
        """ Return owner sidebar navigation for account administration.

        Args:
            request: Current admin request.

        Returns:
            list[dict[str, Any]]: Sidebar navigation groups for the owner site.
        """
        return OwnerTenantSidebarNavigationBuilder.build(request)

    def get_scripts(self, request: HttpRequest) -> list[str]:
        """ Return owner-admin scripts including favicon post-processing.

        Args:
            request: Current admin request.

        Returns:
            list[str]: Owner-admin script asset paths.
        """
        return [
            *super().get_scripts(request),
            static("tenancy/admin/owner/owner_tenant_favicons.js"),
        ]
