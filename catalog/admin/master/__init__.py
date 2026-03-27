""" Master admin registrations for the catalog app. """

from catalog.admin.master.product_image_model_admin import ProductImageModelAdmin
from catalog.admin.master.product_model_admin import ProductModelAdmin
from catalog.admin.master.product_variant_model_admin import ProductVariantModelAdmin

__all__: list[str] = ["ProductModelAdmin", "ProductVariantModelAdmin", "ProductImageModelAdmin"]
