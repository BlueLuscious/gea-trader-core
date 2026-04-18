""" Custom language switching views. """

from urllib.parse import urlsplit, urlunsplit
from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import check_for_language
from django.views import View


class SetAdminLanguageView(View):
    """ Handle admin language changes while normalizing unprefixed default URLs. """

    def post(self, request: HttpRequest) -> HttpResponse:
        """ Persist the selected language and redirect to the normalized admin URL.

        Args:
            request: Current admin request.

        Returns:
            HttpResponse: Redirect response with the language cookie updated.
        """
        next_url = self._get_safe_next_url(request)
        response = HttpResponseRedirect(next_url) if next_url else HttpResponse(status=204)

        lang_code = request.POST.get("language")

        if lang_code and check_for_language(lang_code):
            normalized_next_url = self._normalize_next_url(next_url, lang_code)

            if normalized_next_url != next_url:
                response = HttpResponseRedirect(normalized_next_url)

            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                lang_code,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )

        return response

    def _get_safe_next_url(self, request: HttpRequest) -> str:
        """ Return a safe redirect target from POST data or HTTP referrer.

        Args:
            request: Current admin request.

        Returns:
            str: Safe redirect target.
        """
        next_url = request.POST.get("next", request.GET.get("next"))

        if (
            next_url or request.accepts("text/html")
        ) and not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = request.META.get("HTTP_REFERER")

            if not url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                next_url = "/"

        return next_url or "/"

    def _normalize_next_url(self, next_url: str, language_code: str) -> str:
        """ Return the redirect target for the selected language.

        Args:
            next_url: Current redirect target.
            language_code: Target language code.

        Returns:
            str: Language-normalized redirect target.
        """
        split_result = urlsplit(next_url)
        path = self._strip_language_prefix(split_result.path or "/")

        if language_code != settings.LANGUAGE_CODE:
            path = f"/{language_code}{path}"

        return urlunsplit(
            (
                split_result.scheme,
                split_result.netloc,
                path,
                split_result.query,
                split_result.fragment,
            )
        )

    def _strip_language_prefix(self, path: str) -> str:
        """ Remove any configured language prefix from the given path.

        Args:
            path: Request path to normalize.

        Returns:
            str: Path without a language prefix.
        """
        for code, _label in settings.LANGUAGES:
            prefix = f"/{code}"

            if path == prefix:
                return "/"

            if path.startswith(f"{prefix}/"):
                return path[len(prefix):]

        return path
