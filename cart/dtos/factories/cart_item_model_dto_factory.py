""" Factory helpers for transforming cart items into DTOs. """

from collections.abc import Iterable
from cart.dtos.cart_item_model_dto import CartItemModelDTO
from cart.models import CartItemModel


class CartItemModelDTOFactory:
    """ Factory for transforming cart item models into DTOs. """

    @staticmethod
    def build(instance: CartItemModel) -> CartItemModelDTO:
        """ Build a cart item DTO.

        Args:
            instance: Cart item model instance.

        Returns:
            CartItemModelDTO: Serialized cart item.
        """
        return CartItemModelDTO(
            id=instance.id,
            cart_id=instance.cart_id,
            product_id=instance.product_id,
            variant_id=instance.variant_id,
            quantity=instance.quantity,
            notes=instance.notes,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

    @classmethod
    def build_many(cls, instances: Iterable[CartItemModel]) -> list[CartItemModelDTO]:
        """ Build multiple cart item DTOs.

        Args:
            instances: Iterable of cart item models.

        Returns:
            list[CartItemModelDTO]: DTO list.
        """
        return [cls.build(instance) for instance in instances]
