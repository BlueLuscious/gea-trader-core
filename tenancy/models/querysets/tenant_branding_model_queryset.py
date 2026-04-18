""" Reusable queryset helpers for the tenant-branding model. """

from typing import TYPE_CHECKING
from django.db import models
from django.db.models import Q

if TYPE_CHECKING:
    from tenancy.models import TenantBrandingModel, TenantModel


class TenantBrandingModelQuerySet(models.QuerySet["TenantBrandingModel"]):
    """ QuerySet for reusable tenant-branding filters. """

    def for_tenant(self, tenant: "TenantModel") -> "TenantBrandingModelQuerySet":
        """ Filter branding records belonging to one tenant.

        Args:
            tenant: Tenant whose branding should be returned.

        Returns:
            TenantBrandingModelQuerySet: Branding linked to the provided tenant.
        """
        return self.filter(tenant=tenant)

    def with_tenant(self) -> "TenantBrandingModelQuerySet":
        """ Eager-load the related tenant.

        Returns:
            TenantBrandingModelQuerySet: Branding with ``tenant`` selected.
        """
        return self.select_related("tenant")

    def configured(self) -> "TenantBrandingModelQuerySet":
        """ Filter branding records that already store visible branding data.

        Returns:
            TenantBrandingModelQuerySet: Branding rows with at least one configured field.
        """
        return self.filter(
            Q(display_name__gt="")
            | Q(logo_light__gt="")
            | Q(logo_dark__gt="")
            | Q(icon_light__gt="")
            | Q(icon_dark__gt="")
            | Q(favicon_light__gt="")
            | Q(favicon_dark__gt="")
        )
