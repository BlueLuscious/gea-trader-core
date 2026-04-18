""" Tenancy admin package. """

from tenancy.admin.owner import (
    OwnerTenantSettingsAdmin,
    OwnerTenantSettingsForm,
    TenantBrandingInline,
    TenantBrandingInlineForm,
    TenantBrandingInlineFormSet,
)
from tenancy.admin.master import (
    TenantBrandingModelAdmin,
    TenantGroupModelAdmin,
    TenantMembershipModelAdmin,
    TenantModelAdmin,
)

__all__: list[str] = [
    "OwnerTenantSettingsAdmin",
    "OwnerTenantSettingsForm",
    "TenantBrandingInline",
    "TenantBrandingInlineForm",
    "TenantBrandingInlineFormSet",
    "TenantBrandingModelAdmin",
    "TenantMembershipModelAdmin",
    "TenantGroupModelAdmin",
    "TenantModelAdmin",
]
