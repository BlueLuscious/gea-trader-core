""" Owner-admin tenant settings registration scoped to the active business. """

import logging
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from core.adminsites.site_instances import owner_admin_site
from unfold.admin import ModelAdmin
from tenancy.access.tenant_access_policy import TenantAccessPolicy
from tenancy.admin.owner.owner_tenant_settings_form import OwnerTenantSettingsForm
from tenancy.admin.owner.tenant_branding_inline import TenantBrandingInline
from tenancy.models import TenantModel

logger = logging.getLogger(__name__)


@admin.register(TenantModel, site=owner_admin_site)
class OwnerTenantSettingsAdmin(ModelAdmin):
    """ Native owner-admin change form for the active tenant business settings. """

    class Media:
        """ Owner-admin assets for small business settings refinements. """

        css = {
            "all": ("tenancy/admin/owner/owner_tenant_settings_admin.css",),
        }

    form = OwnerTenantSettingsForm
    inlines = (TenantBrandingInline,)
    readonly_fields = ("name",)
    save_on_top = True
    fieldsets = (
        (
            _("Business"),
            {
                "classes": ("tab",),
                "fields": (
                    "name",
                    ("business_email", "support_email",),
                    ("phone_number", "website_url",),
                ),
            },
        ),
    )

    @staticmethod
    def _can_manage_active_tenant(request: HttpRequest) -> bool:
        """ Return whether the current request may manage the active tenant.

        Args:
            request: Current admin request.

        Returns:
            bool: ``True`` when the current user may manage the active tenant.
        """
        return TenantAccessPolicy.can_manage_tenant(request.user, getattr(request, "tenant", None))

    def has_module_permission(self, request: HttpRequest) -> bool:
        """ Return whether the owner business settings module should be visible.

        Args:
            request: Current admin request.

        Returns:
            bool: ``True`` when the current user may manage the active tenant.
        """
        return self._can_manage_active_tenant(request)

    def has_view_permission(self, request: HttpRequest, obj: TenantModel | None = None) -> bool:
        """ Return whether the current request may view the active tenant settings.

        Args:
            request: Current admin request.
            obj: Tenant being inspected when present.

        Returns:
            bool: ``True`` when the current user may manage the active tenant.
        """
        if obj is None:
            return self._can_manage_active_tenant(request)

        tenant: "TenantModel" = getattr(request, "tenant", None)
        if tenant is None or obj.pk != tenant.pk:
            return False

        return self._can_manage_active_tenant(request)

    def has_change_permission(self, request: HttpRequest, obj: TenantModel | None = None) -> bool:
        """ Return whether the current request may edit the active tenant settings.

        Args:
            request: Current admin request.
            obj: Tenant being edited when present.

        Returns:
            bool: ``True`` when the current user may manage the active tenant.
        """
        if obj is None:
            return self._can_manage_active_tenant(request)

        tenant: "TenantModel" = getattr(request, "tenant", None)
        if tenant is None or obj.pk != tenant.pk:
            return False

        return self._can_manage_active_tenant(request)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """ Return whether the owner business settings screen supports adds.

        Args:
            request: Current admin request.

        Returns:
            bool: Always ``False`` because the screen edits the active tenant only.
        """
        return False

    def has_delete_permission(self, request: HttpRequest, obj: TenantModel | None = None) -> bool:
        """ Return whether the owner business settings screen supports deletes.

        Args:
            request: Current admin request.
            obj: Tenant being inspected when present.

        Returns:
            bool: Always ``False`` because the screen never deletes the active tenant.
        """
        return False

    def get_queryset(self, request: HttpRequest):
        """ Restrict the owner tenant admin to the active tenant only.

        Args:
            request: Current admin request.

        Returns:
            QuerySet[TenantModel]: Active-tenant queryset for owner business settings.
        """
        queryset = super().get_queryset(request)
        tenant: "TenantModel" = getattr(request, "tenant", None)

        if tenant is None or not self._can_manage_active_tenant(request):
            return queryset.none()

        return queryset.filter(pk=tenant.pk)

    def changelist_view(self, request: HttpRequest, extra_context=None):
        """ Redirect the owner tenant changelist to the active tenant change form.

        Args:
            request: Current admin request.
            extra_context: Optional extra context for the admin template.

        Returns:
            HttpResponseRedirect: Redirect response to the active tenant change form.

        Raises:
            PermissionDenied: When the current request may not manage the active tenant.
        """
        if not self._can_manage_active_tenant(request):
            raise PermissionDenied

        tenant = getattr(request, "tenant", None)
        if tenant is None:
            raise PermissionDenied

        logger.info(
            "Redirected owner tenant changelist to active tenant settings tenant_id=%s",
            tenant.pk,
        )
        return redirect(
            reverse(
                "owner_admin:tenancy_tenantmodel_change",
                kwargs={"object_id": str(tenant.pk)},
            )
        )

    def change_view(self, request: HttpRequest, object_id: str, form_url: str = "", extra_context=None):
        """ Render the tenant change form without owner-facing links to the changelist.

        Args:
            request: Current admin request.
            object_id: Tenant primary key from the change URL.
            form_url: Optional custom form action URL.
            extra_context: Optional extra context for the admin template.

        Returns:
            HttpResponse: Native admin change-form response.
        """
        context = {
            "has_view_permission": False,
            "show_back_button": False,
            **(extra_context or {}),
        }
        return super().change_view(request, object_id, form_url, extra_context=context)
