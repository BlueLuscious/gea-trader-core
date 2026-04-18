""" Shared base admin site for project-specific admin sites. """

from typing import Any
from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import get_language
from unfold.sites import UnfoldAdminSite
from unfold.settings import get_config


class BaseAdminSite(UnfoldAdminSite):
    """ Shared project admin site with default Unfold metadata and hooks. """

    site_symbol = ""
    site_url = "/"
    show_languages = True
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
    def get_site_logo(cls, request: HttpRequest) -> dict[str, str] | str | None:
        """ Return the site logo for the current request.

        Args:
            request: Current admin request.

        Returns:
            dict[str, str] | str | None: Theme-aware logo mapping, single URL, or ``None``.
        """
        return None

    @classmethod
    def get_site_icon(cls, request: HttpRequest) -> dict[str, str] | str | None:
        """ Return the site icon for the current request.

        Args:
            request: Current admin request.

        Returns:
            dict[str, str] | str | None: Theme-aware icon mapping, single URL, or ``None``.
        """
        return None

    @classmethod
    def get_site_favicons(cls, request: HttpRequest) -> list[dict[str, str]]:
        """ Return favicon entries for the current request.

        Args:
            request: Current admin request.

        Returns:
            list[dict[str, str]]: Favicon metadata consumed by Unfold.
        """
        return []

    @classmethod
    def get_login_image(cls, request: HttpRequest) -> str | None:
        """ Return the login image for the current request.

        Args:
            request: Current admin request.

        Returns:
            str | None: Login image URL when available.
        """
        return None

    @classmethod
    def get_site_subheader(cls, request: HttpRequest) -> str | None:
        """ Return the site subheader for the current request.

        Args:
            request: Current admin request.

        Returns:
            str | None: Optional site subheader.
        """
        return None

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
    def get_environment(cls, request: HttpRequest) -> list[str] | tuple[str, str] | None:
        """ Return the environment badge shown in the admin header.

        Args:
            request: Current admin request.

        Returns:
            list[str] | tuple[str, str] | None: Label and variant pair, or ``None``.
        """
        return None

    @classmethod
    def get_languages_navigation(cls, request: HttpRequest) -> list[dict[str, str]]:
        """ Return language switcher items sourced from Django settings.

        Args:
            request: Current admin request.

        Returns:
            list[dict[str, str]]: Language metadata for the Unfold switcher.
        """
        current_language = get_language()

        return [
            {
                "code": code,
                "name_local": str(label),
                "name_translated": str(label),
                "active": str(code == current_language).lower(),
            }
            for code, label in settings.LANGUAGES
        ]

    @classmethod
    def get_languages_action(cls, request: HttpRequest) -> str:
        """ Return the URL used by the admin language switcher form.

        Args:
            request: Current admin request.

        Returns:
            str: URL for the admin language switcher endpoint.
        """
        return reverse("set_admin_language")

    @classmethod
    def get_show_languages(cls, request: HttpRequest) -> bool:
        """ Return whether the site should show the language switcher.

        Args:
            request: Current admin request.

        Returns:
            bool: True when the language switcher should be shown.
        """
        return cls.show_languages

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

    def get_site_dropdown(self, request: HttpRequest) -> list[dict[str, Any]]:
        """ Return site dropdown items for the current request.

        Args:
            request: Current admin request.

        Returns:
            list[dict[str, Any]]: Dropdown items rendered by Unfold in the site header.
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

    def _get_list(self, key: str, *args: Any) -> list[Any]:
        """ Resolve one Unfold list setting, including callable root values.

        Args:
            key: Setting key to resolve.
            *args: Runtime arguments forwarded to configured callbacks.

        Returns:
            list[Any]: Resolved list items or an empty list when the configured
            value does not resolve to a list.
        """
        configured_items = get_config(self.settings_name)[key]
        resolved_items = self._get_value(configured_items, *args)

        if not isinstance(resolved_items, list):
            return []

        return [self._get_value(item, *args) for item in resolved_items]
