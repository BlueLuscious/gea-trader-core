""" Shared cart runtime facade for public JSON views. """

from typing import Any
from cart.models import CartItemModel, CartModel
from catalog.models import ProductModel, ProductVariantModel
from front.views.cart.runtime import CartCatalogResolver, CartStateBuilder
from tenancy.models import TenantModel
from .cart_request_mixin import CartRequestMixin
from .cart_resolution_mixin import CartResolutionMixin


class CartRuntimeViewMixin(CartRequestMixin, CartResolutionMixin):
    """ Compose the public cart runtime helpers used by JSON endpoint views. """

    http_method_names = ["get", "post"]
    cart_catalog_resolver_class = CartCatalogResolver
    cart_state_builder_class = CartStateBuilder

    def get_cart_catalog_resolver(self) -> CartCatalogResolver:
        """ Return the catalog resolver used by cart runtime endpoints.

        Returns:
            CartCatalogResolver: Resolver for catalog and cart-item lookups.
        """
        return self.cart_catalog_resolver_class()

    def get_cart_state_builder(self) -> CartStateBuilder:
        """ Return the builder that owns the public cart JSON contract.

        Returns:
            CartStateBuilder: Builder for serialized cart runtime state.
        """
        return self.cart_state_builder_class()

    def get_product(self, tenant: TenantModel, product_id: Any) -> ProductModel | None:
        """ Resolve one active public product for cart runtime usage.

        Args:
            tenant: Public storefront tenant.
            product_id: Incoming product identifier.

        Returns:
            ProductModel | None: Active product or ``None`` when unavailable.
        """
        return self.get_cart_catalog_resolver().get_product(tenant, product_id)

    def get_variant(self, product: ProductModel, variant_id: Any) -> ProductVariantModel | None:
        """ Resolve one active variant for the selected product.

        Args:
            product: Selected public product.
            variant_id: Incoming variant identifier.

        Returns:
            ProductVariantModel | None: Matching active variant or default fallback.
        """
        return self.get_cart_catalog_resolver().get_variant(product, variant_id)

    def get_cart_item(self, cart: CartModel, item_id: Any) -> CartItemModel | None:
        """ Resolve one cart item that belongs to the current active cart.

        Args:
            cart: Active persisted cart.
            item_id: Incoming cart-item identifier.

        Returns:
            CartItemModel | None: Matching cart item or ``None``.
        """
        return self.get_cart_catalog_resolver().get_cart_item(cart, item_id)

    def build_cart_state(self, cart: CartModel | None) -> dict[str, object]:
        """ Build one serialized cart state for the current request.

        Args:
            cart: Persisted active cart when one exists.

        Returns:
            dict[str, object]: Serialized cart state.
        """
        return self.get_cart_state_builder().build_cart_state(cart)
