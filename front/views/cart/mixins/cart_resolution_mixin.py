""" Active-cart resolution helpers for public cart runtime views. """

from datetime import datetime
from django.http import HttpRequest
from django.utils import timezone
from cart.models import CartModel
from cart.settings import CART_RUNTIME_EXPIRATION_HOURS
from front.views.mixins.base import BaseTenantAwareMixin
from tenancy.models import TenantModel


class CartResolutionMixin(BaseTenantAwareMixin):
    """ Resolve or create the active cart for one public request. """

    cart_expiration_hours = CART_RUNTIME_EXPIRATION_HOURS

    def get_new_cart_expiration_time(self) -> datetime:
        """ Return the expiration timestamp assigned to newly created carts.

        Returns:
            datetime: Expiration timestamp for a new runtime cart.
        """
        return timezone.now() + timezone.timedelta(hours=self.cart_expiration_hours)

    def get_active_cart(self, request: HttpRequest, tenant: TenantModel) -> CartModel | None:
        """ Return the current active cart for the request context.

        Args:
            request: Current HTTP request.
            tenant: Public storefront tenant.

        Returns:
            CartModel | None: Active cart or ``None`` when no persisted cart exists.
        """
        session_key = self.ensure_session_key(request)
        queryset = CartModel.objects.for_tenant(tenant).active()
        if request.user.is_authenticated:
            return queryset.for_user(request.user).order_by("-updated_at", "-created_at").first()
        return queryset.for_session(session_key).order_by("-updated_at", "-created_at").first()

    def get_or_create_active_cart(self, request: HttpRequest, tenant: TenantModel) -> CartModel:
        """ Return one persisted active cart for the request context.

        Args:
            request: Current HTTP request.
            tenant: Public storefront tenant.

        Returns:
            CartModel: Existing or newly created active cart.
        """
        existing_cart = self.get_active_cart(request, tenant)
        if existing_cart is not None:
            return existing_cart

        session_key = self.ensure_session_key(request)
        return CartModel.objects.create(
            tenant=tenant,
            user=request.user if request.user.is_authenticated else None,
            session_key=session_key,
            expires_at=self.get_new_cart_expiration_time(),
        )
