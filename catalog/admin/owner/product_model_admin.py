""" Product admin registration for the owner admin site. """

from django.contrib import admin
from django.http import HttpRequest
from unfold.admin import ModelAdmin
from catalog.admin.owner.product_image_model_inline import ProductImageModelInline
from catalog.admin.owner.product_model_admin_form import ProductModelAdminForm
from catalog.admin.owner.product_variant_model_inline import ProductVariantModelInline
from catalog.models import ProductModel
from core.adminsites.site_instances import owner_admin_site


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
            "Product details",
            {
                "classes": ("tab",),
                "description": "Start with the basic information customers and your team will recognize.",
                "fields": (
                    ("name", "slug"),
                    ("brand", "category"),
                ),
            },
        ),
        (
            "Customer-facing content",
            {
                "classes": ("tab",),
                "description": "Write the short and full descriptions your customers will read.",
                "fields": (
                    "short_description",
                    "description",
                ),
            },
        ),
        (
            "Visibility and sales",
            {
                "classes": ("tab",),
                "description": "Control how this product appears and whether it should go through the quote flow.",
                "fields": (
                    "sku_base",
                    ("is_active", "is_featured", "requires_quote"),
                ),
            },
        ),
        (
            "Advanced details",
            {
                "classes": ("tab",),
                "description": "Less frequently used information.",
                "fields": ("created_at", "updated_at"),
            },
        ),
    )
    inlines = (ProductVariantModelInline, ProductImageModelInline)

    def has_delete_permission(self, request: HttpRequest, obj: ProductModel | None = None) -> bool:
        """ Disable hard delete for products in owner admin.

        Args:
            request: Current admin request.
            obj: Product instance when available.

        Returns:
            bool: Always False to prefer deactivation via ``is_active``.
        """
        return False
