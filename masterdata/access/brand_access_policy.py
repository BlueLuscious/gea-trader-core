""" Access policy helpers for tenant-scoped brand administration. """

from typing import TYPE_CHECKING
from django.http import HttpRequest
from tenancy.access.tenant_access_policy import TenantAccessPolicy

if TYPE_CHECKING:
    from masterdata.models import BrandModel


class BrandAccessPolicy:
    """ Resolve access to tenant-scoped brand flows inside the owner admin. """

    view_permission = "masterdata.view_brandmodel"
    add_permission = "masterdata.add_brandmodel"
    change_permission = "masterdata.change_brandmodel"
    delete_permission = "masterdata.delete_brandmodel"

    @classmethod
    def can_access_brands(cls, request: HttpRequest) -> bool:
        """ Return whether the current request may access brand flows.

        Args:
            request: Current HTTP request.

        Returns:
            bool: ``True`` when the actor belongs to the active tenant and can view brands.
        """
        return cls._can_access_with_permission(request, cls.view_permission)

    @classmethod
    def can_add_brand(cls, request: HttpRequest) -> bool:
        """ Return whether the current request may create brands.

        Args:
            request: Current HTTP request.

        Returns:
            bool: ``True`` when the actor belongs to the active tenant and can add brands.
        """
        return cls._can_access_with_permission(request, cls.add_permission)

    @classmethod
    def can_view_brand(cls, request: HttpRequest, brand: "BrandModel | None") -> bool:
        """ Return whether one brand should be visible inside the active tenant.

        Args:
            request: Current HTTP request.
            brand: Brand being inspected.

        Returns:
            bool: ``True`` when the actor may access the brand and the brand belongs
            to the active tenant.
        """
        return cls._can_access_brand_object(request, brand, cls.view_permission)

    @classmethod
    def can_change_brand(cls, request: HttpRequest, brand: "BrandModel | None") -> bool:
        """ Return whether one brand may be edited inside the active tenant.

        Args:
            request: Current HTTP request.
            brand: Brand being inspected.

        Returns:
            bool: ``True`` when the actor may edit brands in the active tenant.
        """
        return cls._can_access_brand_object(request, brand, cls.change_permission)

    @classmethod
    def can_delete_brand(cls, request: HttpRequest, brand: "BrandModel | None") -> bool:
        """ Return whether one brand may be deleted inside the active tenant.

        Args:
            request: Current HTTP request.
            brand: Brand being inspected.

        Returns:
            bool: ``True`` when the actor may delete brands in the active tenant.
        """
        return cls._can_access_brand_object(request, brand, cls.delete_permission)

    @classmethod
    def _can_access_brand_object(
        cls,
        request: HttpRequest,
        brand: "BrandModel | None",
        permission: str,
    ) -> bool:
        """ Return whether one brand belongs to the active tenant under one permission check.

        Args:
            request: Current HTTP request.
            brand: Brand being inspected.
            permission: Django permission codename required for the action.

        Returns:
            bool: ``True`` when the actor passes the base permission check and the
            brand stays in scope.
        """
        if brand is None:
            return False

        tenant = getattr(request, "tenant", None)
        if tenant is None or brand.tenant_id != tenant.pk:
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
