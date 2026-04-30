""" Base operational helpers for tenant-aware public storefront views. """

from django.http import Http404, HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from tenancy.models import TenantModel


class BaseTenantAwareMixin:
    """ Resolve the active public tenant and ensure request-level storefront state. """

    request: HttpRequest

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args: object, **kwargs: object):
        """ Ensure public storefront responses emit a CSRF cookie.

        Args:
            request: Current HTTP request.
            *args: Positional dispatch arguments.
            **kwargs: Keyword dispatch arguments.

        Returns:
            HttpResponse: View dispatch result.
        """
        return super().dispatch(request, *args, **kwargs)

    def get_tenant(self) -> TenantModel:
        """ Return the single active tenant that owns the public site.

        Returns:
            TenantModel: Active tenant used by the public site.

        Raises:
            Http404: When no active tenant is available for the public site.
        """
        tenant = TenantModel.objects.filter(is_active=True).order_by("created_at", "name").first()
        if tenant is None:
            raise Http404("No public tenant is available.")

        return tenant

    @staticmethod
    def ensure_session_key(request: HttpRequest) -> str:
        """ Ensure the provided request owns one Django session key.

        Args:
            request: Current HTTP request.

        Returns:
            str: Current request session key.
        """
        if request.session.session_key:
            return request.session.session_key

        request.session.create()
        return request.session.session_key or ""
