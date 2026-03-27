""" Catalog admin package. """

from catalog.admin.master import ProductImageModelAdmin, ProductModelAdmin, ProductVariantModelAdmin
from catalog.admin.owner import ProductModelAdmin as OwnerProductModelAdmin

__all__: list[str] = [
    "ProductModelAdmin",
    "ProductVariantModelAdmin",
    "ProductImageModelAdmin",
    "OwnerProductModelAdmin",
]
