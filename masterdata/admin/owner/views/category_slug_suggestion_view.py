""" Owner-admin JSON view for category slug suggestions. """

from typing import TYPE_CHECKING
from django.http import HttpRequest, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views import View
from masterdata.access import CategoryAccessPolicy
from masterdata.admin.owner.category_slug_suggestion_builder import CategorySlugSuggestionBuilder

if TYPE_CHECKING:
    from tenancy.models import TenantModel


class CategorySlugSuggestionView(View):
    """ Return tenant-unique category slug suggestions for owner admin. """

    http_method_names = ["get"]

    def get(self, request: HttpRequest) -> JsonResponse:
        """ Return one tenant-unique category slug suggestion.

        Args:
            request: Current owner-admin request.

        Returns:
            JsonResponse: Suggested slug payload or an access error payload.
        """
        tenant: "TenantModel | None" = getattr(request, "tenant", None)
        if tenant is None or not CategoryAccessPolicy.can_access_categories(request):
            return JsonResponse(
                {"error": _("Category slug suggestions require an active business.")},
                status=403,
            )

        suggested_slug = CategorySlugSuggestionBuilder.build(
            tenant=tenant,
            name=request.GET.get("name", ""),
            parent_id=request.GET.get("parent", ""),
            parent_slug=request.GET.get("parent_slug", ""),
            exclude_id=request.GET.get("object_id", ""),
        )
        return JsonResponse({"slug": suggested_slug})
