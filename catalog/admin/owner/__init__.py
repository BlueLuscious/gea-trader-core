""" Owner admin registrations for the catalog app. """

from catalog.admin.owner.product_image_model_inline import ProductImageModelInline
from catalog.admin.owner.product_image_model_inline_formset import ProductImageModelInlineFormSet
from catalog.admin.owner.product_model_admin import ProductModelAdmin
from catalog.admin.owner.product_model_admin_form import ProductModelAdminForm
from catalog.admin.owner.product_variant_model_inline import ProductVariantModelInline
from catalog.admin.owner.product_variant_model_inline_form import ProductVariantModelInlineForm
from catalog.admin.owner.product_variant_model_inline_formset import ProductVariantModelInlineFormSet

__all__: list[str] = [
    "ProductModelAdmin",
    "ProductModelAdminForm",
    "ProductVariantModelInline",
    "ProductVariantModelInlineForm",
    "ProductVariantModelInlineFormSet",
    "ProductImageModelInline",
    "ProductImageModelInlineFormSet",
]
