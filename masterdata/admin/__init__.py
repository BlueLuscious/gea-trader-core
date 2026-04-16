""" Masterdata admin package. """

from masterdata.admin.master import BrandModelAdmin as MasterBrandModelAdmin
from masterdata.admin.master import CategoryModelAdmin as MasterCategoryModelAdmin
from masterdata.admin.owner import BrandModelAdmin as OwnerBrandModelAdmin
from masterdata.admin.owner import CategoryModelAdmin as OwnerCategoryModelAdmin

__all__: list[str] = [
    "MasterBrandModelAdmin",
    "MasterCategoryModelAdmin",
    "OwnerBrandModelAdmin",
    "OwnerCategoryModelAdmin",
]
