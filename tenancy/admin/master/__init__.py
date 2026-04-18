""" Master admin registrations for the tenancy app. """

from .tenant_branding_model_admin import TenantBrandingModelAdmin
from .tenant_membership_model_admin import TenantMembershipModelAdmin
from .tenant_group_model_admin import TenantGroupModelAdmin
from .tenant_model_admin import TenantModelAdmin

__all__: list[str] = [
    "TenantBrandingModelAdmin",
    "TenantMembershipModelAdmin",
    "TenantGroupModelAdmin",
    "TenantModelAdmin",
]
