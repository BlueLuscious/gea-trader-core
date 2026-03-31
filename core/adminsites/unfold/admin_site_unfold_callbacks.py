""" Request-aware Unfold callbacks for project admin sites. """

from django.http import HttpRequest
from django.utils.module_loading import import_string
from core.adminsites.admin_namespace import AdminNamespace
from core.adminsites.registry import ADMIN_SITE_INSTANCE_REGISTRY
from core.adminsites.sites.base_admin_site import BaseAdminSite


class AdminSiteUnfoldCallbacks:
    """ Resolve admin site instances and expose request-aware Unfold callbacks. """

    @classmethod
    def site_title(cls, request: HttpRequest) -> str:
        """ Return the site title for the current request.

        Args:
            request: Current admin request.

        Returns:
            str: Resolved site title.
        """
        site_instance = cls._resolve_admin_site_instance(request)
        return site_instance.get_site_title(request)

    @classmethod
    def site_header(cls, request: HttpRequest) -> str:
        """ Return the site header for the current request.

        Args:
            request: Current admin request.

        Returns:
            str: Resolved site header.
        """
        site_instance = cls._resolve_admin_site_instance(request)
        return site_instance.get_site_header(request)

    @classmethod
    def site_symbol(cls, request: HttpRequest) -> str:
        """ Return the site symbol for the current request.

        Args:
            request: Current admin request.

        Returns:
            str: Resolved site symbol.
        """
        site_instance = cls._resolve_admin_site_instance(request)
        return site_instance.get_site_symbol(request)

    @classmethod
    def site_url(cls, request: HttpRequest) -> str:
        """ Return the site URL for the current request.

        Args:
            request: Current admin request.

        Returns:
            str: Resolved site URL.
        """
        site_instance = cls._resolve_admin_site_instance(request)
        return site_instance.get_site_url(request)

    @classmethod
    def show_search(cls, request: HttpRequest) -> bool:
        """ Return whether the sidebar search should be visible.

        Args:
            request: Current admin request.

        Returns:
            bool: True when search should be shown.
        """
        site_instance = cls._resolve_admin_site_instance(request)
        return site_instance.get_show_sidebar_search(request)

    @classmethod
    def show_all_applications(cls, request: HttpRequest) -> bool:
        """ Return whether all applications should be visible in the sidebar.

        Args:
            request: Current admin request.

        Returns:
            bool: True when all applications should be shown.
        """
        site_instance = cls._resolve_admin_site_instance(request)
        return site_instance.get_show_all_applications(request)

    @classmethod
    def sidebar_navigation(cls, request: HttpRequest) -> list[dict[str, object]]:
        """ Return sidebar navigation for the current request.

        Args:
            request: Current admin request.

        Returns:
            list[dict[str, object]]: Resolved sidebar navigation items.
        """
        site_instance = cls._resolve_admin_site_instance(request)
        return site_instance.get_sidebar_navigation(request)

    @classmethod
    def scripts(cls, request: HttpRequest) -> list[str]:
        """ Return additional Unfold script paths for the current request.

        Args:
            request: Current admin request.

        Returns:
            list[str]: Script asset paths.
        """
        site_instance = cls._resolve_admin_site_instance(request)
        return site_instance.get_scripts(request)

    @classmethod
    def styles(cls, request: HttpRequest) -> list[str]:
        """ Return additional Unfold style paths for the current request.

        Args:
            request: Current admin request.

        Returns:
            list[str]: Style asset paths.
        """
        site_instance = cls._resolve_admin_site_instance(request)
        return site_instance.get_styles(request)

    @classmethod
    def _resolve_admin_site_instance(cls, request: HttpRequest) -> BaseAdminSite:
        """ Resolve the current admin site instance from the request.

        Args:
            request: Current HTTP request.

        Returns:
            BaseAdminSite: Resolved admin site instance.
        """
        namespace = cls._resolve_admin_namespace(request) or AdminNamespace.MASTER
        return cls._resolve_admin_site_instance_for_namespace(namespace)

    @classmethod
    def _resolve_admin_namespace(cls, request: HttpRequest) -> AdminNamespace | None:
        """ Resolve the current admin namespace from the request.

        Args:
            request: Current HTTP request.

        Returns:
            AdminNamespace | None: Resolved namespace when available.
        """
        resolver_match = request.resolver_match

        if resolver_match is None or not resolver_match.namespace:
            return None

        try:
            return AdminNamespace(resolver_match.namespace)
        except ValueError:
            return None

    @classmethod
    def _resolve_admin_site_instance_for_namespace(cls, namespace: AdminNamespace) -> BaseAdminSite:
        """ Resolve an admin site instance from an explicit namespace.

        Args:
            namespace: Target admin namespace.

        Returns:
            BaseAdminSite: Resolved admin site instance.
        """
        return import_string(ADMIN_SITE_INSTANCE_REGISTRY[namespace])
