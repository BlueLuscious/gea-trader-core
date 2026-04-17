""" Product admin registration for the owner admin site. """

import logging
from typing import TYPE_CHECKING
from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from catalog.access import CatalogAccessPolicy
from catalog.admin.owner.product_image_model_inline import ProductImageModelInline
from catalog.admin.owner.product_model_admin_form import ProductModelAdminForm
from catalog.admin.owner.product_variant_model_inline import ProductVariantModelInline
from catalog.models import ProductModel
from core.adminsites.site_instances import owner_admin_site

if TYPE_CHECKING:
    from catalog.models.querysets import ProductModelQuerySet
    from tenancy.models.tenant_model import TenantModel

logger = logging.getLogger(__name__)


@admin.register(ProductModel, site=owner_admin_site)
class ProductModelAdmin(ModelAdmin):
    """ Guided owner admin for products with variants and images in one screen. """

    class Media:
        """ Load owner-specific assets for the product admin layout. """

        css = {
            "all": ("catalog/admin/owner/product_model_admin.css",),
        }

    form = ProductModelAdminForm
    list_display = ("name", "brand", "category", "is_active", "is_featured", "updated_at")
    list_filter = ("is_active", "is_featured", "requires_quote", "brand", "category")
    search_fields = ("name", "slug", "sku_base")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_select_related = ("brand", "category")
    save_on_top = True
    fieldsets = (
        (
            _("Product details"),
            {
                "classes": ("tab",),
                "description": _("Start with the basic information customers and your team will recognize."),
                "fields": (
                    ("name", "slug"),
                    ("brand", "category"),
                ),
            },
        ),
        (
            _("Customer-facing content"),
            {
                "classes": ("tab",),
                "description": _("Write the short and full descriptions your customers will read."),
                "fields": (
                    "short_description",
                    "description",
                ),
            },
        ),
        (
            _("Visibility and sales"),
            {
                "classes": ("tab",),
                "description": _(
                    "Control whether customers request a quote or can buy directly. "
                    "Purchasable products need a priced default variant."
                ),
                "fields": (
                    "sku_base",
                    ("is_active", "is_featured", "requires_quote"),
                ),
            },
        ),
        (
            _("Advanced details"),
            {
                "classes": ("tab",),
                "description": _("Less frequently used information."),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )
    inlines = (ProductVariantModelInline, ProductImageModelInline)

    def get_queryset(self, request: HttpRequest) -> "ProductModelQuerySet":
        """ Return only products that belong to the active tenant.

        Args:
            request: Current admin request.

        Returns:
            QuerySet[ProductModel]: Tenant-scoped product queryset.
        """
        tenant: "TenantModel | None" = getattr(request, "tenant", None)
        if tenant is None:
            logger.info("Returned no owner-visible products because no active tenant is bound to the request")
            return ProductModel.objects.none()

        tenant_queryset = super().get_queryset(request).for_tenant(tenant).with_related()
        logger.info(
            "Scoped owner product queryset tenant_id=%s product_count=%s",
            tenant.pk,
            tenant_queryset.count(),
        )
        return tenant_queryset

    def save_model(
        self,
        request: HttpRequest,
        obj: ProductModel,
        form: ProductModelAdminForm,
        change: bool,
    ) -> None:
        """ Persist products under the active tenant in owner admin.

        Args:
            request: Current admin request.
            obj: Product being saved.
            form: Bound admin form.
            change: Whether the object already exists.
        """
        if not change:
            obj.tenant = getattr(request, "tenant", None)

        super().save_model(request, obj, form, change)
        logger.info(
            "Saved owner product tenant_id=%s product_id=%s change=%s",
            getattr(obj.tenant, "pk", None),
            obj.pk,
            change,
        )

    def has_module_permission(self, request: HttpRequest) -> bool:
        """ Return whether the catalog module should appear in owner admin.

        Args:
            request: Current admin request.

        Returns:
            bool: ``True`` when the actor may access catalog flows.
        """
        return CatalogAccessPolicy.can_access_catalog(request)

    def has_view_permission(self, request: HttpRequest, obj: ProductModel | None = None) -> bool:
        """ Return whether the current request may view products in owner admin.

        Args:
            request: Current admin request.
            obj: Product instance when available.

        Returns:
            bool: ``True`` when the actor may view the catalog module or one in-scope product.
        """
        if obj is None:
            return CatalogAccessPolicy.can_access_catalog(request)

        return CatalogAccessPolicy.can_view_product(request, obj)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """ Return whether the current request may create products.

        Args:
            request: Current admin request.

        Returns:
            bool: ``True`` when the actor may add products in the active tenant.
        """
        return CatalogAccessPolicy.can_add_product(request)

    def has_change_permission(self, request: HttpRequest, obj: ProductModel | None = None) -> bool:
        """ Return whether the current request may edit products in owner admin.

        Args:
            request: Current admin request.
            obj: Product instance when available.

        Returns:
            bool: ``True`` when the actor may change the catalog module or one in-scope product.
        """
        if obj is None:
            return CatalogAccessPolicy.can_access_catalog(request)

        return CatalogAccessPolicy.can_change_product(request, obj)

    def has_delete_permission(self, request: HttpRequest, obj: ProductModel | None = None) -> bool:
        """ Disable hard delete for products in owner admin.

        Args:
            request: Current admin request.
            obj: Product instance when available.

        Returns:
            bool: Always False to prefer deactivation via ``is_active``.
        """
        return False
