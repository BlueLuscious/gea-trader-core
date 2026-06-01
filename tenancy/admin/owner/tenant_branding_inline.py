""" Inline used by the owner tenant settings screen for branding. """

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from unfold.admin import StackedInline
from tenancy.access.tenant_access_policy import TenantAccessPolicy
from tenancy.admin.owner.tenant_branding_inline_form import TenantBrandingInlineForm
from tenancy.admin.owner.tenant_branding_inline_formset import TenantBrandingInlineFormSet
from tenancy.models import TenantBrandingModel


class TenantBrandingInline(StackedInline):
    """ Edit one branding record for the tenant active in owner admin. """

    model = TenantBrandingModel
    form = TenantBrandingInlineForm
    formset = TenantBrandingInlineFormSet
    tab = True
    extra = 1
    min_num = 1
    max_num = 1
    can_delete = False
    verbose_name = _("Business branding")
    verbose_name_plural = _("Business branding")
    fieldsets = (
        (
            _("Display"),
            {
                "description": _("Control the name shown when branding is rendered for this business."),
                "fields": (
                    ("display_name",),
                ),
            },
        ),
        (
            _("Visual assets"),
            {
                "description": _("Upload light and dark variants so each surface can pick the best fit."),
                "fields": (
                    ("logo_light", "logo_dark",),
                    ("icon_light", "icon_dark",),
                    ("favicon_light", "favicon_dark",),
                ),
            },
        ),
        (
            _("Social links"),
            {
                "description": _("Optional public social profiles shown on storefront contact surfaces."),
                "fields": (
                    ("instagram_url", "facebook_url",),
                    ("linkedin_url",),
                ),
            },
        ),
    )

    def has_view_permission(self, request: HttpRequest, obj=None) -> bool:
        """ Return whether the current request may view tenant branding.

        Args:
            request: Current admin request.
            obj: Parent tenant instance when present.

        Returns:
            bool: ``True`` when the current user may manage the active tenant.
        """
        return TenantAccessPolicy.can_manage_tenant(request.user, getattr(request, "tenant", None))

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        """ Return whether the current request may edit tenant branding.

        Args:
            request: Current admin request.
            obj: Parent tenant instance when present.

        Returns:
            bool: ``True`` when the current user may manage the active tenant.
        """
        return TenantAccessPolicy.can_manage_tenant(request.user, getattr(request, "tenant", None))

    def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
        """ Return whether the current request may create tenant branding.

        Args:
            request: Current admin request.
            obj: Parent tenant instance when present.

        Returns:
            bool: ``True`` when the current user may manage the active tenant.
        """
        return TenantAccessPolicy.can_manage_tenant(request.user, getattr(request, "tenant", None))
