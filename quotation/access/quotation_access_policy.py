""" Access policy helpers for tenant-scoped quotation administration. """

from typing import TYPE_CHECKING
from django.http import HttpRequest
from tenancy.access.tenant_access_policy import TenantAccessPolicy

if TYPE_CHECKING:
    from quotation.models import QuoteItemModel, QuoteModel


class QuotationAccessPolicy:
    """ Resolve access to tenant-scoped quotation flows inside the owner admin. """

    view_permission = "quotation.view_quotemodel"
    add_permission = "quotation.add_quotemodel"
    change_permission = "quotation.change_quotemodel"
    delete_permission = "quotation.delete_quotemodel"
    view_item_permission = "quotation.view_quoteitemmodel"

    @classmethod
    def can_access_quotation(cls, request: HttpRequest) -> bool:
        """ Return whether the current request may access quotation flows.

        Args:
            request: Current HTTP request.

        Returns:
            bool: ``True`` when the actor belongs to the active tenant and can view quotes.
        """
        return cls._can_access_with_permission(request, cls.view_permission)

    @classmethod
    def can_add_quote(cls, request: HttpRequest) -> bool:
        """ Return whether the current request may create quotes.

        Args:
            request: Current HTTP request.

        Returns:
            bool: ``True`` when the actor belongs to the active tenant and can add quotes.
        """
        return cls._can_access_with_permission(request, cls.add_permission)

    @classmethod
    def can_view_quote(cls, request: HttpRequest, quote: "QuoteModel | None") -> bool:
        """ Return whether one quote should be visible inside the active tenant.

        Args:
            request: Current HTTP request.
            quote: Quote being inspected.

        Returns:
            bool: ``True`` when the actor may access quotation flows and the quote belongs to the active tenant.
        """
        return cls._can_access_quote_object(request, quote, cls.view_permission)

    @classmethod
    def can_change_quote(cls, request: HttpRequest, quote: "QuoteModel | None") -> bool:
        """ Return whether one quote may be edited inside the active tenant.

        Args:
            request: Current HTTP request.
            quote: Quote being inspected.

        Returns:
            bool: ``True`` when the actor may edit quotes in the active tenant.
        """
        return cls._can_access_quote_object(request, quote, cls.change_permission)

    @classmethod
    def can_delete_quote(cls, request: HttpRequest, quote: "QuoteModel | None") -> bool:
        """ Return whether one quote may be deleted inside the active tenant.

        Args:
            request: Current HTTP request.
            quote: Quote being inspected.

        Returns:
            bool: ``True`` when the actor may delete quotes in the active tenant.
        """
        return cls._can_access_quote_object(request, quote, cls.delete_permission)

    @classmethod
    def can_view_quote_item(cls, request: HttpRequest, item: "QuoteItemModel | None") -> bool:
        """ Return whether one quote item should be visible inside the active tenant.

        Args:
            request: Current HTTP request.
            item: Quote item being inspected.

        Returns:
            bool: ``True`` when the actor may view quote items and the parent quote belongs to the active tenant.
        """
        if item is None:
            return False

        return cls._can_access_quote_object(request, item.quote, cls.view_item_permission)

    @classmethod
    def _can_access_quote_object(
        cls,
        request: HttpRequest,
        quote: "QuoteModel | None",
        permission: str,
    ) -> bool:
        """ Return whether one quote belongs to the active tenant under one permission check.

        Args:
            request: Current HTTP request.
            quote: Quote being inspected.
            permission: Django permission codename required for the action.

        Returns:
            bool: ``True`` when the actor passes the base permission check and the quote stays in scope.
        """
        if quote is None:
            return False

        tenant = getattr(request, "tenant", None)
        if tenant is None or quote.tenant_id != tenant.pk:
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
