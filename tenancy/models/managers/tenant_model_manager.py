""" Custom manager for the tenant model. """

from typing import TYPE_CHECKING
from django.db import models
from tenancy.models.querysets.tenant_model_queryset import TenantModelQuerySet

if TYPE_CHECKING:
    from accounts.models import UserModel
    from tenancy.models import TenantModel


class TenantModelManager(models.Manager["TenantModel"]):
    """ Manager exposing typed tenant queryset helpers. """

    def get_queryset(self) -> TenantModelQuerySet:
        """ Return the base queryset for tenant queries.

        Returns:
            TenantModelQuerySet: Specialized queryset for TenantModel.
        """
        return TenantModelQuerySet(self.model, using=self._db)

    def active(self) -> TenantModelQuerySet:
        """ Return active tenants only.

        Returns:
            TenantModelQuerySet: Active tenants.
        """
        return self.get_queryset().active()

    def for_user(self, user: "UserModel") -> TenantModelQuerySet:
        """ Return tenants related to one user.

        Args:
            user: User whose tenants should be returned.

        Returns:
            TenantModelQuerySet: Tenants linked to the provided user.
        """
        return self.get_queryset().for_user(user)
