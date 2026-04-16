from collections.abc import Iterable
from cart.dtos.cart_model_dto import CartModelDTO
from cart.models import CartModel


class CartModelDTOFactory:
    """ Factory for transforming cart models into DTOs. """

    @staticmethod
    def build(instance: CartModel) -> CartModelDTO:
        """ Build a cart DTO.

        Args:
            instance: Cart model instance.

        Returns:
            CartModelDTO: Serialized cart.
        """
        return CartModelDTO(
            id=instance.id,
            tenant_id=str(instance.tenant_id),
            user_id=instance.user_id,
            session_key=instance.session_key,
            status=instance.status,
            expires_at=instance.expires_at,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

    @classmethod
    def build_many(cls, instances: Iterable[CartModel]) -> list[CartModelDTO]:
        """ Build multiple cart DTOs.

        Args:
            instances: Iterable of cart models.

        Returns:
            list[CartModelDTO]: DTO list.
        """
        return [cls.build(instance) for instance in instances]
