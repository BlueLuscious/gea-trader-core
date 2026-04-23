""" Shared cart runtime helpers for public JSON views. """

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

from django.http import HttpRequest, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse

from cart.models import CartItemModel, CartModel
from catalog.models import ProductModel, ProductVariantModel
from front.views.public_site_view_mixin import PublicSiteViewMixin
from tenancy.models import TenantModel


class CartRuntimeViewMixin(PublicSiteViewMixin):
    """ Provide shared cart runtime helpers for public storefront JSON views. """

    http_method_names = ["get", "post"]

    def ensure_session_key(self, request: HttpRequest) -> str:
        """ Ensure the incoming request owns one Django session key.

        Args:
            request: Current HTTP request.

        Returns:
            str: Persisted Django session key.
        """
        if request.session.session_key:
            return request.session.session_key

        request.session.create()
        return request.session.session_key or ""

    def get_request_payload(self, request: HttpRequest) -> dict[str, Any]:
        """ Parse one JSON request body into a dictionary.

        Args:
            request: Current HTTP request.

        Returns:
            dict[str, Any]: Parsed request payload or an empty dictionary.
        """
        if not request.body:
            return {}

        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (TypeError, ValueError):
            return {}

        return payload if isinstance(payload, dict) else {}

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
        )

    def get_product(self, tenant: TenantModel, product_id: Any) -> ProductModel | None:
        """ Resolve one active public product for cart runtime usage.

        Args:
            tenant: Public storefront tenant.
            product_id: Incoming product identifier.

        Returns:
            ProductModel | None: Active product or ``None`` when unavailable.
        """
        if not product_id:
            return None

        return (
            ProductModel.objects.for_tenant(tenant)
            .active()
            .with_related()
            .prefetch_related("images", "variants")
            .filter(pk=product_id)
            .first()
        )

    def get_variant(self, product: ProductModel, variant_id: Any) -> ProductVariantModel | None:
        """ Resolve one active variant for the selected product.

        Args:
            product: Selected public product.
            variant_id: Incoming variant identifier.

        Returns:
            ProductVariantModel | None: Matching active variant or default fallback.
        """
        if variant_id:
            return product.variants.active().filter(pk=variant_id).first()
        return product.variants.active().filter(is_default=True).order_by("sort_order", "name", "id").first()

    def get_cart_item(self, cart: CartModel, item_id: Any) -> CartItemModel | None:
        """ Resolve one cart item that belongs to the current active cart.

        Args:
            cart: Active persisted cart.
            item_id: Incoming cart-item identifier.

        Returns:
            CartItemModel | None: Matching cart item or ``None``.
        """
        if not item_id:
            return None

        return CartItemModel.objects.for_cart(cart).with_catalog().filter(pk=item_id).first()

    def build_cart_item_payload(self, item: CartItemModel) -> dict[str, object]:
        """ Build one serialized cart-item payload for the public sidebar.

        Args:
            item: Persisted cart item.

        Returns:
            dict[str, object]: Serialized item ready for runtime rendering.
        """
        product = item.product
        variant = item.variant
        resolved_price = variant.price if variant is not None else product.get_public_price()
        image_url = product.get_variant_image_url(variant) if variant is not None else product.get_preferred_image_url()
        title = product.name
        subtitle = variant.name if variant is not None and variant.name else ""
        return {
            "id": item.id,
            "product_id": product.id,
            "variant_id": variant.id if variant is not None else None,
            "title": title,
            "subtitle": subtitle,
            "sku": variant.sku if variant is not None else product.sku_base,
            "image_url": image_url,
            "href": reverse("product_detail", kwargs={"slug": product.slug}),
            "quantity": item.quantity,
            "price": str(resolved_price) if resolved_price is not None else "",
            "price_text": (
                f"ARS {resolved_price:.2f}"
                if isinstance(resolved_price, Decimal)
                else ""
            ),
            "notes": item.notes,
        }

    def build_cart_state(self, cart: CartModel | None) -> dict[str, object]:
        """ Build one serialized cart state for the current request.

        Args:
            cart: Persisted active cart when one exists.

        Returns:
            dict[str, object]: Serialized cart state.
        """
        if cart is None:
            return {
                "cart_id": None,
                "status": "",
                "items": [],
                "count": 0,
                "items_html": "",
                "summary_html": "",
            }

        items = [
            self.build_cart_item_payload(item)
            for item in CartItemModel.objects.for_cart(cart).with_catalog().order_by("created_at", "id")
        ]
        line_count = len(items)
        return {
            "cart_id": cart.id,
            "status": cart.status,
            "items": items,
            "count": line_count,
            "items_html": self.build_cart_items_html(items),
            "summary_html": self.build_cart_summary_html(count=line_count),
        }

    def build_error_response(self, message: str, status: int = 400) -> JsonResponse:
        """ Build one small error response for cart runtime operations.

        Args:
            message: Public-facing error detail.
            status: HTTP status code to return.

        Returns:
            JsonResponse: Error response payload.
        """
        return JsonResponse({"error": message}, status=status)

    def build_cart_items_html(self, items: list[dict[str, object]]) -> str:
        """ Render cart-item HTML for the sidebar body.

        Args:
            items: Serialized cart-item payloads.

        Returns:
            str: Rendered cart items HTML.
        """
        return "".join(
            render_to_string("cart/runtime/cart_item.html", {"item": item})
            for item in items
        )

    def build_cart_summary_html(self, *, count: int) -> str:
        """ Render the cart summary block for the sidebar body.

        Args:
            count: Total cart line count.

        Returns:
            str: Rendered summary HTML.
        """
        return render_to_string(
            "cart/runtime/cart_summary.html",
            {
                "count": count,
            },
        )
