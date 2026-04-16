""" Brand admin registration for the owner admin site. """

from typing import TYPE_CHECKING
from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from core.adminsites.site_instances import owner_admin_site
from masterdata.access import BrandAccessPolicy
from masterdata.models import BrandModel

if TYPE_CHECKING:
    from masterdata.models.querysets.brand_model_queryset import BrandModelQuerySet
    from tenancy.models import TenantModel


@admin.register(BrandModel, site=owner_admin_site)
class BrandModelAdmin(ModelAdmin):
    """ Guided owner admin for tenant-scoped brand reference data. """

    list_display = ("name", "slug", "is_active", "updated_at")
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("name", "slug")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    save_on_top = True
    fieldsets = (
        (
            _("Brand details"),
            {
                "classes": ("tab",),
                "description": _("Create reusable brand references for the active business catalog."),
                "fields": (
                    ("name", "slug"),
                    "description",
                    "is_active",
                ),
            },
        ),
        (
            _("Advanced details"),
            {
                "classes": ("tab",),
                "description": _("Read-only audit details for this brand."),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    def get_queryset(self, request: HttpRequest) -> "BrandModelQuerySet":
        """ Return only brands that belong to the active tenant.

        Args:
            request: Current admin request.

        Returns:
            QuerySet[BrandModel]: Tenant-scoped brand queryset.
        """
        tenant: "TenantModel | None" = getattr(request, "tenant", None)
        if tenant is None:
            return BrandModel.objects.none()

        return super().get_queryset(request).for_tenant(tenant)

    def save_model(self, request: HttpRequest, obj: BrandModel, form, change: bool) -> None:
        """ Persist brands under the active tenant in owner admin.

        Args:
            request: Current admin request.
            obj: Brand being saved.
            form: Bound admin form.
            change: Whether the object already exists.
        """
        if not change:
            obj.tenant = getattr(request, "tenant", None)

        super().save_model(request, obj, form, change)

    def has_module_permission(self, request: HttpRequest) -> bool:
        """ Return whether the brand module should appear in owner admin.

        Args:
            request: Current admin request.

        Returns:
            bool: ``True`` when the actor may access brand flows.
        """
        return BrandAccessPolicy.can_access_brands(request)

    def has_view_permission(self, request: HttpRequest, obj: BrandModel | None = None) -> bool:
        """ Return whether the current request may view brands in owner admin.

        Args:
            request: Current admin request.
            obj: Brand instance when available.

        Returns:
            bool: ``True`` when the actor may view the brand module or one in-scope brand.
        """
        if obj is None:
            return BrandAccessPolicy.can_access_brands(request)

        return BrandAccessPolicy.can_view_brand(request, obj)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """ Return whether the current request may create brands.

        Args:
            request: Current admin request.

        Returns:
            bool: ``True`` when the actor may add brands in the active tenant.
        """
        return BrandAccessPolicy.can_add_brand(request)

    def has_change_permission(self, request: HttpRequest, obj: BrandModel | None = None) -> bool:
        """ Return whether the current request may edit brands in owner admin.

        Args:
            request: Current admin request.
            obj: Brand instance when available.

        Returns:
            bool: ``True`` when the actor may change the brand module or one in-scope brand.
        """
        if obj is None:
            return BrandAccessPolicy.can_access_brands(request)

        return BrandAccessPolicy.can_change_brand(request, obj)

    def has_delete_permission(self, request: HttpRequest, obj: BrandModel | None = None) -> bool:
        """ Disable hard delete for brands in owner admin.

        Args:
            request: Current admin request.
            obj: Brand instance when available.

        Returns:
            bool: Always ``False`` to prefer deactivation via ``is_active``.
        """
        return False
