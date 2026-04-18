""" Access policy helpers for tenant-scoped accounts administration. """

from typing import TYPE_CHECKING
from django.apps import apps
from django.http import HttpRequest
from tenancy.access.tenant_access_policy import TenantAccessPolicy
from tenancy.choices import TenantRole

if TYPE_CHECKING:
    from django.contrib.auth.models import Group
    from accounts.models import UserModel


class AccountsAccessPolicy:
    """ Resolve access to owner-managed users and groups inside one tenant. """

    view_user_permission = "accounts.view_usermodel"
    add_user_permission = "accounts.add_usermodel"
    change_user_permission = "accounts.change_usermodel"
    delete_user_permission = "accounts.delete_usermodel"
    view_group_permission = "auth.view_group"
    add_group_permission = "auth.add_group"
    change_group_permission = "auth.change_group"
    delete_group_permission = "auth.delete_group"
    visible_user_roles = (TenantRole.OWNER, TenantRole.OPERATOR)

    @classmethod
    def can_manage_accounts(cls, request: HttpRequest) -> bool:
        """ Return whether the current request may manage tenant-scoped accounts.

        Args:
            request: Current HTTP request.

        Returns:
            bool: ``True`` when the request user may manage owner accounts in the active tenant.
        """
        return TenantAccessPolicy.can_manage_tenant(request.user, getattr(request, "tenant", None))

    @classmethod
    def can_access_users(cls, request: HttpRequest) -> bool:
        """ Return whether the current request may access tenant-scoped user flows.

        Args:
            request: Current HTTP request.

        Returns:
            bool: ``True`` when the actor may view tenant-scoped users.
        """
        return cls._can_access_with_permission(request, cls.view_user_permission)

    @classmethod
    def can_add_user(cls, request: HttpRequest) -> bool:
        """ Return whether the current request may create tenant-scoped users.

        Args:
            request: Current HTTP request.

        Returns:
            bool: ``True`` when the actor may add tenant-scoped users.
        """
        return cls._can_access_with_permission(request, cls.add_user_permission)

    @classmethod
    def can_view_user(cls, request: HttpRequest, user: "UserModel | None") -> bool:
        """ Return whether one target user should be visible in owner accounts admin.

        Args:
            request: Current HTTP request.
            user: User being inspected.

        Returns:
            bool: ``True`` when the user belongs to the active tenant in one visible role.
        """
        if user is None:
            return False

        if not cls._can_access_with_permission(request, cls.view_user_permission):
            return False

        tenant = getattr(request, "tenant", None)
        if tenant is None or getattr(user, "is_superuser", False):
            return False

        return user.tenant_memberships.filter(
            tenant=tenant,
            role__in=cls.visible_user_roles,
        ).exists()

    @classmethod
    def can_change_user(cls, request: HttpRequest, user: "UserModel | None") -> bool:
        """ Return whether one target user may be edited in owner accounts admin.

        Args:
            request: Current HTTP request.
            user: User being inspected.

        Returns:
            bool: ``True`` when the actor may change tenant-scoped users and the user stays visible.
        """
        if not cls._can_access_with_permission(request, cls.change_user_permission):
            return False

        return cls._can_access_user_object(request, user)

    @classmethod
    def can_delete_user(cls, request: HttpRequest, user: "UserModel | None") -> bool:
        """ Return whether one target user may be deleted in owner accounts admin.

        Args:
            request: Current HTTP request.
            user: User being inspected.

        Returns:
            bool: ``True`` when the actor may delete tenant-scoped users and the user stays visible.
        """
        if not cls._can_access_with_permission(request, cls.delete_user_permission):
            return False

        return cls._can_access_user_object(request, user)

    @classmethod
    def can_access_groups(cls, request: HttpRequest) -> bool:
        """ Return whether the current request may access tenant-scoped group flows.

        Args:
            request: Current HTTP request.

        Returns:
            bool: ``True`` when the actor may view tenant-scoped groups.
        """
        return cls._can_access_with_permission(request, cls.view_group_permission)

    @classmethod
    def can_add_group(cls, request: HttpRequest) -> bool:
        """ Return whether the current request may create tenant-scoped groups.

        Args:
            request: Current HTTP request.

        Returns:
            bool: ``True`` when the actor may add tenant-scoped groups.
        """
        return cls._can_access_with_permission(request, cls.add_group_permission)

    @classmethod
    def can_view_group(cls, request: HttpRequest, group: "Group | None") -> bool:
        """ Return whether one target group should be visible in owner accounts admin.

        Args:
            request: Current HTTP request.
            group: Group being inspected.

        Returns:
            bool: ``True`` when the group belongs to the active tenant and the actor may manage accounts.
        """
        if group is None:
            return False

        if not cls._can_access_with_permission(request, cls.view_group_permission):
            return False

        return cls._can_access_group_object(request, group)

    @classmethod
    def can_change_group(cls, request: HttpRequest, group: "Group | None") -> bool:
        """ Return whether one target group may be edited in owner accounts admin.

        Args:
            request: Current HTTP request.
            group: Group being inspected.

        Returns:
            bool: ``True`` when the actor may change tenant-scoped groups and the group stays visible.
        """
        if not cls._can_access_with_permission(request, cls.change_group_permission):
            return False

        return cls._can_access_group_object(request, group)

    @classmethod
    def can_delete_group(cls, request: HttpRequest, group: "Group | None") -> bool:
        """ Return whether one target group may be deleted in owner accounts admin.

        Args:
            request: Current HTTP request.
            group: Group being inspected.

        Returns:
            bool: ``True`` when the actor may delete tenant-scoped groups and the group stays visible.
        """
        if not cls._can_access_with_permission(request, cls.delete_group_permission):
            return False

        return cls._can_access_group_object(request, group)

    @classmethod
    def _can_access_with_permission(cls, request: HttpRequest, permission: str) -> bool:
        """ Return whether the request passes the base tenant and Django permission checks.

        Args:
            request: Current HTTP request.
            permission: Django permission codename required for the action.

        Returns:
            bool: ``True`` when the actor may manage accounts in the active tenant and holds the permission.
        """
        return cls.can_manage_accounts(request) and request.user.has_perm(permission)

    @classmethod
    def _can_access_user_object(cls, request: HttpRequest, user: "UserModel | None") -> bool:
        """ Return whether one user stays visible in the active tenant scope.

        Args:
            request: Current HTTP request.
            user: User being inspected.

        Returns:
            bool: ``True`` when the user belongs to the active tenant in one visible role.
        """
        tenant = getattr(request, "tenant", None)
        if tenant is None or user is None or getattr(user, "is_superuser", False):
            return False

        return user.tenant_memberships.filter(
            tenant=tenant,
            role__in=cls.visible_user_roles,
        ).exists()

    @classmethod
    def _can_access_group_object(cls, request: HttpRequest, group: "Group | None") -> bool:
        """ Return whether one group stays visible in the active tenant scope.

        Args:
            request: Current HTTP request.
            group: Group being inspected.

        Returns:
            bool: ``True`` when the group belongs to the active tenant.
        """
        tenant = getattr(request, "tenant", None)
        if tenant is None or group is None:
            return False

        return apps.get_model("tenancy", "TenantGroupModel").objects.filter(tenant=tenant, group=group).exists()
