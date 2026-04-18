""" Core access policy helpers for tenant-scoped memberships and roles. """

from typing import TYPE_CHECKING
from django.apps import apps
from tenancy.choices import TenantRole

if TYPE_CHECKING:
    from collections.abc import Iterable
    from accounts.models import UserModel
    from tenancy.models import TenantMembershipModel, TenantModel
    from tenancy.models.querysets import TenantMembershipModelQuerySet


class TenantAccessPolicy:
    """ Resolve whether one user belongs to one tenant with one or more roles. """

    @classmethod
    def can_access_tenant(cls, user: "UserModel", tenant: "TenantModel | None") -> bool:
        """ Return whether one authenticated user may access one tenant context.

        Args:
            user: User being evaluated.
            tenant: Tenant currently in scope.

        Returns:
            bool: ``True`` when the user is a superuser or has one active membership in the tenant.
        """
        if not cls._is_authenticated(user) or tenant is None:
            return False

        if getattr(user, "is_superuser", False):
            return True

        return cls._get_memberships(user, tenant).exists()

    @classmethod
    def has_role(cls, user: "UserModel", tenant: "TenantModel | None", role: TenantRole) -> bool:
        """ Return whether one authenticated user has one exact active tenant role.

        Args:
            user: User being evaluated.
            tenant: Tenant currently in scope.
            role: Role required for the check.

        Returns:
            bool: ``True`` when the user is a superuser or holds the role in the tenant.
        """
        return cls.has_any_role(user, tenant, (role,))

    @classmethod
    def has_any_role(
        cls,
        user: "UserModel",
        tenant: "TenantModel | None",
        roles: "Iterable[TenantRole]",
    ) -> bool:
        """ Return whether one authenticated user has any active tenant role from one set.

        Args:
            user: User being evaluated.
            tenant: Tenant currently in scope.
            roles: Acceptable tenant roles.

        Returns:
            bool: ``True`` when the user is a superuser or matches one role from the set.
        """
        if not cls._is_authenticated(user) or tenant is None:
            return False

        if getattr(user, "is_superuser", False):
            return True

        return cls._get_memberships(user, tenant).filter(role__in=tuple(roles)).exists()

    @classmethod
    def can_manage_tenant(cls, user: "UserModel", tenant: "TenantModel | None") -> bool:
        """ Return whether one user may manage owner-scoped resources for one tenant.

        Args:
            user: User being evaluated.
            tenant: Tenant currently in scope.

        Returns:
            bool: ``True`` when the user is a superuser or an active tenant owner.
        """
        return cls.has_role(user, tenant, TenantRole.OWNER)

    @staticmethod
    def _is_authenticated(user: object) -> bool:
        """ Return whether one user object represents an authenticated actor.

        Args:
            user: User object being evaluated.

        Returns:
            bool: ``True`` when the user is authenticated and not anonymous.
        """
        return bool(getattr(user, "is_authenticated", False))

    @staticmethod
    def _get_memberships(user: "UserModel", tenant: "TenantModel") -> "TenantMembershipModelQuerySet":
        """ Return active memberships for one user within one tenant.

        Args:
            user: User being evaluated.
            tenant: Tenant currently in scope.

        Returns:
            QuerySet[TenantMembershipModel]: Active memberships for the user in the tenant.
        """
        membership: "TenantMembershipModel" = apps.get_model("tenancy", "TenantMembershipModel")
        return membership.objects.for_user_active_tenants(user).for_tenant(tenant)
