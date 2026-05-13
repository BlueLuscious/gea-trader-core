""" Catalog lookup collaborator for public cart runtime views. """

from typing import Any
from cart.models import CartItemModel, CartModel
from catalog.models import ProductModel, ProductVariantModel
from tenancy.models import TenantModel


class CartCatalogResolver:
    """ Resolve products, variants, and cart items for public cart endpoints. """

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
