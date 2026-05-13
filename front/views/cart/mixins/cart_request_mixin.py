""" Request helpers for public cart runtime views. """

import json
from typing import Any
from django.http import HttpRequest, JsonResponse


class CartRequestMixin:
    """ Parse public cart requests and build small HTTP error payloads. """

    def get_request_payload(self, request: HttpRequest) -> dict[str, Any]:
        """ Parse one JSON request body into a dictionary.

        Args:
            request: Current HTTP request.

        Returns:
            dict[str, Any]: Parsed request payload or an empty dictionary.
        """
        if not request.body:
            return {}

        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (TypeError, ValueError):
            return {}

        return payload if isinstance(payload, dict) else {}

    def build_error_response(self, message: str, status: int = 400) -> JsonResponse:
        """ Build one small error response for cart runtime operations.

        Args:
            message: Public-facing error detail.
            status: HTTP status code to return.

        Returns:
            JsonResponse: Error response payload.
        """
        return JsonResponse({"error": message}, status=status)
