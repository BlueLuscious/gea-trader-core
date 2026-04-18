""" Custom manager for the user model. """

from typing import TYPE_CHECKING
from django.contrib.auth.models import UserManager
from accounts.models.querysets.user_model_queryset import UserModelQuerySet

if TYPE_CHECKING:
    from accounts.models.user_model import UserModel
    from tenancy.models import TenantModel


class UserModelManager(UserManager["UserModel"]):
    """ Manager exposing Django auth behavior plus typed user queryset helpers. """

    def get_queryset(self) -> UserModelQuerySet:
        """ Return the base queryset for user queries.

        Returns:
            UserModelQuerySet: A specialized queryset for UserModel.
        """
        return UserModelQuerySet(self.model, using=self._db)

    def for_tenant(self, tenant: "TenantModel") -> UserModelQuerySet:
        """ Return users related to one tenant.

        Args:
            tenant: Tenant whose users should be returned.

        Returns:
            UserModelQuerySet: Users linked to the provided tenant.
        """
        return self.get_queryset().for_tenant(tenant)

    def with_tenants(self) -> UserModelQuerySet:
        """ Prefetch tenant relations for user queries.

        Returns:
            UserModelQuerySet: Users with tenant relations prefetched.
        """
        return self.get_queryset().with_tenants()
