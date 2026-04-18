""" Reusable queryset helpers for the tenant model. """

from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from accounts.models import UserModel
    from tenancy.models import TenantModel


class TenantModelQuerySet(models.QuerySet["TenantModel"]):
    """ QuerySet for reusable tenant filters. """

    def active(self) -> "TenantModelQuerySet":
        """ Filter tenants that remain active.

        Returns:
            TenantModelQuerySet: Active tenants only.
        """
        return self.filter(is_active=True)

    def for_user(self, user: "UserModel") -> "TenantModelQuerySet":
        """ Filter tenants related to a given user through memberships.

        Args:
            user: User whose tenants should be returned.

        Returns:
            TenantModelQuerySet: Tenants linked to the provided user.
        """
        return self.filter(memberships__user=user).distinct()
