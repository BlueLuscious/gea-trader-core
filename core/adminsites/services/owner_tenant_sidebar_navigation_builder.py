""" Service for building the owner tenant sidebar navigation. """

from typing import Any, TYPE_CHECKING
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from catalog.access.catalog_access_policy import CatalogAccessPolicy
from quotation.access.quotation_access_policy import QuotationAccessPolicy
from tenancy.access.tenant_accounts_access_policy import TenantAccountsAccessPolicy
from tenancy.access.tenant_access_policy import TenantAccessPolicy

if TYPE_CHECKING:
    from tenancy.models.tenant_membership_model import TenantModel


class OwnerTenantSidebarNavigationBuilder:
    """ Build sidebar navigation groups for the owner admin site. """

    @staticmethod
    def get_business_settings_link(request: HttpRequest) -> str:
        """ Return the owner business settings link for the active tenant.

        Args:
            request: Current admin request.

        Returns:
            str: Tenant change URL for the active tenant or the owner index when
            there is no tenant in context.
        """
        tenant: "TenantModel" = getattr(request, "tenant", None)
        tenant_id: str = getattr(tenant, "pk", None)

        if tenant_id is None:
            return reverse("owner_admin:index")

        return reverse(
            "owner_admin:tenancy_tenantmodel_change",
            kwargs={"object_id": str(tenant_id)},
        )

    @classmethod
    def build(cls, request: HttpRequest) -> list[dict[str, Any]]:
        """ Build owner sidebar navigation for account administration.

        Args:
            request: Current admin request.

        Returns:
            list[dict[str, Any]]: Sidebar navigation groups for the owner site.
        """
        return [
            {
                "title": _("Business"),
                "items": [
                    {
                        "title": _("Settings"),
                        "icon": "storefront",
                        "link": cls.get_business_settings_link(request),
                        "permission": lambda req: (
                            TenantAccessPolicy.can_manage_tenant(req.user, getattr(req, "tenant", None))
                        ),
                    },
                ],
            },
            {
                "title": _("Accounts"),
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "group",
                        "link": reverse("owner_admin:accounts_usermodel_changelist"),
                        "permission": lambda req: (
                            TenantAccountsAccessPolicy.can_manage_accounts(req)
                            and req.user.has_perm("accounts.view_usermodel")
                        ),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "admin_panel_settings",
                        "link": reverse("owner_admin:auth_group_changelist"),
                        "permission": lambda req: (
                            TenantAccountsAccessPolicy.can_manage_accounts(req)
                            and req.user.has_perm("auth.view_group")
                        ),
                    },
                ],
            },
            {
                "title": _("Catalog"),
                "items": [
                    {
                        "title": _("Products"),
                        "icon": "inventory_2",
                        "link": reverse("owner_admin:catalog_productmodel_changelist"),
                        "permission": lambda req: CatalogAccessPolicy.can_access_catalog(req),
                    },
                ],
            },
            {
                "title": _("Sales"),
                "items": [
                    {
                        "title": _("Quotes"),
                        "icon": "request_quote",
                        "link": reverse("owner_admin:quotation_quotemodel_changelist"),
                        "permission": lambda req: QuotationAccessPolicy.can_access_quotation(req),
                    },
                ],
            },
        ]
