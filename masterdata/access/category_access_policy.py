""" Access policy helpers for tenant-scoped category administration. """

from typing import TYPE_CHECKING
from django.http import HttpRequest
from tenancy.access.tenant_access_policy import TenantAccessPolicy

if TYPE_CHECKING:
    from masterdata.models import CategoryModel


class CategoryAccessPolicy:
    """ Resolve access to tenant-scoped category flows inside the owner admin. """

    view_permission = "masterdata.view_categorymodel"
    add_permission = "masterdata.add_categorymodel"
    change_permission = "masterdata.change_categorymodel"
    delete_permission = "masterdata.delete_categorymodel"

    @classmethod
    def can_access_categories(cls, request: HttpRequest) -> bool:
        """ Return whether the current request may access category flows.

        Args:
            request: Current HTTP request.

        Returns:
            bool: ``True`` when the actor belongs to the active tenant and can view categories.
        """
        return cls._can_access_with_permission(request, cls.view_permission)

    @classmethod
    def can_add_category(cls, request: HttpRequest) -> bool:
        """ Return whether the current request may create categories.

        Args:
            request: Current HTTP request.

        Returns:
            bool: ``True`` when the actor belongs to the active tenant and can add categories.
        """
        return cls._can_access_with_permission(request, cls.add_permission)

    @classmethod
    def can_view_category(cls, request: HttpRequest, category: "CategoryModel | None") -> bool:
        """ Return whether one category should be visible inside the active tenant.

        Args:
            request: Current HTTP request.
            category: Category being inspected.

        Returns:
            bool: ``True`` when the actor may access the category and the category
            belongs to the active tenant.
        """
        return cls._can_access_category_object(request, category, cls.view_permission)

    @classmethod
    def can_change_category(cls, request: HttpRequest, category: "CategoryModel | None") -> bool:
        """ Return whether one category may be edited inside the active tenant.

        Args:
            request: Current HTTP request.
            category: Category being inspected.

        Returns:
            bool: ``True`` when the actor may edit categories in the active tenant.
        """
        return cls._can_access_category_object(request, category, cls.change_permission)

    @classmethod
    def can_delete_category(cls, request: HttpRequest, category: "CategoryModel | None") -> bool:
        """ Return whether one category may be deleted inside the active tenant.

        Args:
            request: Current HTTP request.
            category: Category being inspected.

        Returns:
            bool: ``True`` when the actor may delete categories in the active tenant.
        """
        return cls._can_access_category_object(request, category, cls.delete_permission)

    @classmethod
    def _can_access_category_object(
        cls,
        request: HttpRequest,
        category: "CategoryModel | None",
        permission: str,
    ) -> bool:
        """ Return whether one category belongs to the active tenant under one permission check.

        Args:
            request: Current HTTP request.
            category: Category being inspected.
            permission: Django permission codename required for the action.

        Returns:
            bool: ``True`` when the actor passes the base permission check and the
            category stays in scope.
        """
        if category is None:
            return False

        tenant = getattr(request, "tenant", None)
        if tenant is None or category.tenant_id != tenant.pk:
            return False

        return cls._can_access_with_permission(request, permission)

    @classmethod
    def _can_access_with_permission(cls, request: HttpRequest, permission: str) -> bool:
        """ Return whether the request passes the base tenant and Django permission checks.

        Args:
            request: Current HTTP request.
            permission: Django permission codename required for the action.

        Returns:
            bool: ``True`` when the actor belongs to the active tenant and holds the permission.
        """
        tenant = getattr(request, "tenant", None)
        return (
            TenantAccessPolicy.can_access_tenant(request.user, tenant)
            and request.user.has_perm(permission)
        )
