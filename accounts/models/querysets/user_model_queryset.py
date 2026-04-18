""" Reusable queryset helpers for the user model. """

from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from accounts.models.user_model import UserModel
    from tenancy.models import TenantModel


class UserModelQuerySet(models.QuerySet["UserModel"]):
    """ QuerySet for reusable user filters. """

    def for_tenant(self, tenant: "TenantModel") -> "UserModelQuerySet":
        """ Filter users linked to one tenant through memberships.

        Args:
            tenant: Tenant whose users should be returned.

        Returns:
            UserModelQuerySet: Users linked to the provided tenant.
        """
        return self.filter(tenant_memberships__tenant=tenant).distinct()

    def with_tenants(self) -> "UserModelQuerySet":
        """ Prefetch tenant memberships and tenant relations for user queries.

        Returns:
            UserModelQuerySet: Users with tenant relations prefetched.
        """
        return self.prefetch_related("tenant_memberships__tenant")
