""" Factory helpers for building quote-item snapshots from cart items. """

from cart.models import CartItemModel
from quotation.models import QuoteItemModel, QuoteModel


class QuoteItemSnapshotFactory:
    """ Build quote-item snapshots from runtime cart items. """

    @staticmethod
    def build(*, quote: QuoteModel, cart_item: CartItemModel) -> QuoteItemModel:
        """ Build one unsaved quote-item snapshot from one cart item.

        Args:
            quote: Newly created quote root.
            cart_item: Runtime cart item to snapshot.

        Returns:
            QuoteItemModel: Unsaved quote-item snapshot.
        """
        product = cart_item.product
        variant = cart_item.variant
        unit_price = variant.price if variant is not None else product.get_public_price()
        return QuoteItemModel(
            quote=quote,
            product=product,
            variant=variant,
            product_name_snapshot=product.name,
            sku_snapshot=variant.effective_sku if variant is not None else product.sku_base,
            attributes_snapshot=dict(variant.attributes_json or {}) if variant is not None else {},
            unit_price_snapshot=unit_price,
            quantity=cart_item.quantity,
            notes=cart_item.notes,
        )
