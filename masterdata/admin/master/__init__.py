""" Master admin registrations for the masterdata app. """

from masterdata.admin.master.brand_model_admin import BrandModelAdmin
from masterdata.admin.master.category_model_admin import CategoryModelAdmin

__all__: list[str] = ["BrandModelAdmin", "CategoryModelAdmin"]
