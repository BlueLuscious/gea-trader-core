""" Master admin site definition. """

from typing import Any
from django.http import HttpRequest
from core.adminsites.sites.base_admin_site import BaseAdminSite


class MasterAdminSite(BaseAdminSite):
    """ Full admin site reserved for technical platform administrators. """

    settings_name = "MASTER_ADMIN_UNFOLD"
    site_header = "Master Administration"
    site_title = "Master Admin"
    site_symbol = "shield_person"
    index_title = "Platform administration"
    show_all_applications = True

    def get_sidebar_navigation(self, request: HttpRequest) -> list[dict[str, Any]]:
        """ Return dynamic master admin sidebar navigation.

        Args:
            request: Current admin request.

        Returns:
            list[dict[str, Any]]: Sidebar navigation groups for the master site.
        """
        app_list = self.get_app_list(request)
        return [self._build_sidebar_group(app_config) for app_config in app_list]

    def _build_sidebar_group(self, app_config: dict[str, Any]) -> dict[str, Any]:
        """ Build one sidebar group from a Django admin app entry.

        Args:
            app_config: Django admin application entry from ``get_app_list``.

        Returns:
            dict[str, Any]: Unfold sidebar group configuration.
        """
        return {
            "title": app_config["name"],
            "items": [self._build_sidebar_item(model_config) for model_config in app_config["models"]],
        }

    def _build_sidebar_item(self, model_config: dict[str, Any]) -> dict[str, Any]:
        """ Build one sidebar item from a Django admin model entry.

        Args:
            model_config: Django admin model entry from ``get_app_list``.

        Returns:
            dict[str, Any]: Unfold sidebar item configuration.
        """
        return {
            "title": model_config["name"],
            "icon": "lens",
            "link": model_config["admin_url"],
        }

    def has_permission(self, request: HttpRequest) -> bool:
        """ Return whether the request user can access the master admin site.

        Args:
            request: Current admin request.

        Returns:
            bool: True when the request user is an active superuser.
        """
        user = request.user
        return bool(user.is_active and user.is_superuser)
