""" Owner admin registrations for the masterdata app. """

from masterdata.admin.owner.brand_model_admin import BrandModelAdmin
from masterdata.admin.owner.category_model_admin import CategoryModelAdmin

__all__: list[str] = ["BrandModelAdmin", "CategoryModelAdmin"]
