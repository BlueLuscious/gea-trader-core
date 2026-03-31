""" Owner admin site definition. """

from django.http import HttpRequest
from core.adminsites.sites.base_admin_site import BaseAdminSite


class OwnerAdminSite(BaseAdminSite):
    """ Guided admin site intended for business owners and operators. """

    settings_name = "OWNER_ADMIN_UNFOLD"
    site_header = "GEA Owner Administration"
    site_title = "GEA Owner Admin"
    site_symbol = "storefront"
    index_title = "Business operations"

    def has_permission(self, request: HttpRequest) -> bool:
        """ Return whether the request user can access the owner admin site.

        Args:
            request: Current admin request.

        Returns:
            bool: True when the request user is an active staff user.
        """
        user = request.user
        return bool(user.is_active and user.is_staff)
