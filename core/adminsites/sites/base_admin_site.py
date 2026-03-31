""" Shared base admin site for project-specific admin sites. """

from typing import Any
from django.http import HttpRequest
from unfold.sites import UnfoldAdminSite


class BaseAdminSite(UnfoldAdminSite):
    """ Shared project admin site with default Unfold metadata and hooks. """

    site_symbol = ""
    site_url = "/"
    show_all_applications = False
    show_sidebar_search = True
    dashboard_callback: str | None = None

    @classmethod
    def get_site_title(cls, request: HttpRequest) -> str:
        """ Return the site title for the current request.

        Args:
            request: Current admin request.

        Returns:
            str: Site title.
        """
        return cls.site_title

    @classmethod
    def get_site_header(cls, request: HttpRequest) -> str:
        """ Return the site header for the current request.

        Args:
            request: Current admin request.

        Returns:
            str: Site header.
        """
        return cls.site_header

    @classmethod
    def get_site_symbol(cls, request: HttpRequest) -> str:
        """ Return the site symbol for the current request.

        Args:
            request: Current admin request.

        Returns:
            str: Site symbol.
        """
        return cls.site_symbol

    @classmethod
    def get_site_url(cls, request: HttpRequest) -> str:
        """ Return the site URL for the current request.

        Args:
            request: Current admin request.

        Returns:
            str: Site URL.
        """
        return cls.site_url

    @classmethod
    def get_show_all_applications(cls, request: HttpRequest) -> bool:
        """ Return whether the site should show all applications.

        Args:
            request: Current admin request.

        Returns:
            bool: True when all applications should be shown.
        """
        return cls.show_all_applications

    @classmethod
    def get_show_sidebar_search(cls, request: HttpRequest) -> bool:
        """ Return whether the site should show sidebar search.

        Args:
            request: Current admin request.

        Returns:
            bool: True when sidebar search should be shown.
        """
        return cls.show_sidebar_search

    def get_sidebar_navigation(self, request: HttpRequest) -> list[dict[str, Any]]:
        """ Return sidebar navigation items for the current request.

        Args:
            request: Current admin request.

        Returns:
            list[dict[str, Any]]: Sidebar navigation items.
        """
        return []

    def get_scripts(self, request: HttpRequest) -> list[str]:
        """ Return additional Unfold script paths for the current request.

        Args:
            request: Current admin request.

        Returns:
            list[str]: Script asset paths.
        """
        return []

    def get_styles(self, request: HttpRequest) -> list[str]:
        """ Return additional Unfold style paths for the current request.

        Args:
            request: Current admin request.

        Returns:
            list[str]: Style asset paths.
        """
        return []
