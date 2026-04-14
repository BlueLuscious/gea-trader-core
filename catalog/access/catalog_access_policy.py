""" Access policy helpers for tenant-scoped catalog administration. """

from typing import TYPE_CHECKING
from django.http import HttpRequest
from tenancy.access.tenant_access_policy import TenantAccessPolicy

if TYPE_CHECKING:
    from catalog.models import ProductModel


class CatalogAccessPolicy:
    """ Resolve access to tenant-scoped catalog flows inside the owner admin. """

    view_permission = "catalog.view_productmodel"
    add_permission = "catalog.add_productmodel"
    change_permission = "catalog.change_productmodel"
    delete_permission = "catalog.delete_productmodel"

    @classmethod
    def can_access_catalog(cls, request: HttpRequest) -> bool:
        """ Return whether the current request may access catalog flows.

        Args:
            request: Current HTTP request.

        Returns:
            bool: ``True`` when the actor belongs to the active tenant and can view products.
        """
        return cls._can_access_with_permission(request, cls.view_permission)

    @classmethod
    def can_add_product(cls, request: HttpRequest) -> bool:
        """ Return whether the current request may create products.

        Args:
            request: Current HTTP request.

        Returns:
            bool: ``True`` when the actor belongs to the active tenant and can add products.
        """
        return cls._can_access_with_permission(request, cls.add_permission)

    @classmethod
    def can_view_product(cls, request: HttpRequest, product: "ProductModel | None") -> bool:
        """ Return whether one product should be visible inside the active tenant.

        Args:
            request: Current HTTP request.
            product: Product being inspected.

        Returns:
            bool: ``True`` when the actor may access catalog flows and the product belongs to the active tenant.
        """
        return cls._can_access_object(request, product, cls.view_permission)

    @classmethod
    def can_change_product(cls, request: HttpRequest, product: "ProductModel | None") -> bool:
        """ Return whether one product may be edited inside the active tenant.

        Args:
            request: Current HTTP request.
            product: Product being inspected.

        Returns:
            bool: ``True`` when the actor may edit products in the active tenant.
        """
        return cls._can_access_object(request, product, cls.change_permission)

    @classmethod
    def can_delete_product(cls, request: HttpRequest, product: "ProductModel | None") -> bool:
        """ Return whether one product may be deleted inside the active tenant.

        Args:
            request: Current HTTP request.
            product: Product being inspected.

        Returns:
            bool: ``True`` when the actor may delete products in the active tenant.
        """
        return cls._can_access_object(request, product, cls.delete_permission)

    @classmethod
    def _can_access_object(
        cls,
        request: HttpRequest,
        product: "ProductModel | None",
        permission: str,
    ) -> bool:
        """ Return whether one product belongs to the active tenant under one permission check.

        Args:
            request: Current HTTP request.
            product: Product being inspected.
            permission: Django permission codename required for the action.

        Returns:
            bool: ``True`` when the actor passes the base permission check and the product stays in scope.
        """
        if product is None:
            return False

        tenant = getattr(request, "tenant", None)
        if tenant is None or product.tenant_id != tenant.pk:
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
