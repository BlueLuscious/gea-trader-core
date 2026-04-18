""" Site-based Unfold settings adapter. """

from typing import Any
from django.utils.module_loading import import_string
from core.adminsites.admin_namespace import AdminNamespace
from core.adminsites.registry import ADMIN_SITE_CLASS_REGISTRY
from core.adminsites.sites.base_admin_site import BaseAdminSite
from core.adminsites.unfold.admin_site_unfold_callbacks import AdminSiteUnfoldCallbacks


class AdminSiteUnfoldSettings:
    """ Build an Unfold settings dictionary from an admin site class. """

    def __init__(self, site_class: type[BaseAdminSite]) -> None:
        """ Store the admin site class used as the settings source of truth.

        Args:
            site_class: Admin site class that provides metadata and hooks.
        """
        self.site_class = site_class

    @classmethod
    def for_namespace(cls, namespace: AdminNamespace) -> "AdminSiteUnfoldSettings":
        """ Build the adapter for one admin namespace.

        Args:
            namespace: Target admin namespace.

        Returns:
            AdminSiteUnfoldSettings: Adapter bound to the resolved admin site class.
        """
        site_class = cls._resolve_admin_site_class_for_namespace(namespace)
        return cls(site_class)

    def build(self) -> dict[str, Any]:
        """ Build the Unfold settings dictionary for the admin site class.

        Returns:
            dict[str, Any]: Unfold settings dictionary.
        """
        return {
            "SITE_TITLE": AdminSiteUnfoldCallbacks.site_title,
            "SITE_HEADER": AdminSiteUnfoldCallbacks.site_header,
            "SITE_SUBHEADER": AdminSiteUnfoldCallbacks.site_subheader,
            "SITE_LOGO": AdminSiteUnfoldCallbacks.site_logo,
            "SITE_ICON": AdminSiteUnfoldCallbacks.site_icon,
            "SITE_SYMBOL": AdminSiteUnfoldCallbacks.site_symbol,
            "SITE_FAVICONS": AdminSiteUnfoldCallbacks.site_favicons,
            "SITE_URL": AdminSiteUnfoldCallbacks.site_url,
            "ENVIRONMENT": AdminSiteUnfoldCallbacks.environment,
            "LOGIN": {
                "image": AdminSiteUnfoldCallbacks.login_image,
            },
            "SHOW_LANGUAGES": AdminSiteUnfoldCallbacks.show_languages,
            "LANGUAGES": {
                "action": AdminSiteUnfoldCallbacks.languages_action,
                "navigation": AdminSiteUnfoldCallbacks.languages_navigation,
            },
            "SITE_DROPDOWN": AdminSiteUnfoldCallbacks.site_dropdown,
            "SIDEBAR": {
                "show_search": AdminSiteUnfoldCallbacks.show_search,
                "show_all_applications": AdminSiteUnfoldCallbacks.show_all_applications,
                "navigation": AdminSiteUnfoldCallbacks.sidebar_navigation,
            },
            "SCRIPTS": AdminSiteUnfoldCallbacks.scripts,
            "STYLES": AdminSiteUnfoldCallbacks.styles,
            "DASHBOARD_CALLBACK": self.site_class.dashboard_callback,
        }

    @classmethod
    def _resolve_admin_site_class_for_namespace(cls, namespace: AdminNamespace) -> type[BaseAdminSite]:
        """ Resolve an admin site class from an explicit namespace.

        Args:
            namespace: Target admin namespace.

        Returns:
            type[BaseAdminSite]: Resolved admin site class.
        """
        return import_string(ADMIN_SITE_CLASS_REGISTRY[namespace])
