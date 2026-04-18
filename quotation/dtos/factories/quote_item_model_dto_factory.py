""" Factory helpers for transforming quote items into DTOs. """

from collections.abc import Iterable
from quotation.dtos.quote_item_model_dto import QuoteItemModelDTO
from quotation.models import QuoteItemModel


class QuoteItemModelDTOFactory:
    """ Factory for transforming quote item models into DTOs. """

    @staticmethod
    def build(instance: QuoteItemModel) -> QuoteItemModelDTO:
        """ Build a quote item DTO.

        Args:
            instance: Quote item model instance.

        Returns:
            QuoteItemModelDTO: Serialized quote item.
        """
        return QuoteItemModelDTO(
            id=instance.id,
            quote_id=instance.quote_id,
            product_id=instance.product_id,
            variant_id=instance.variant_id,
            product_name_snapshot=instance.product_name_snapshot,
            sku_snapshot=instance.sku_snapshot,
            attributes_snapshot=dict(instance.attributes_snapshot or {}),
            unit_price_snapshot=instance.unit_price_snapshot,
            quantity=instance.quantity,
            notes=instance.notes,
            created_at=instance.created_at,
        )

    @classmethod
    def build_many(cls, instances: Iterable[QuoteItemModel]) -> list[QuoteItemModelDTO]:
        """ Build multiple quote item DTOs.

        Args:
            instances: Iterable of quote item models.

        Returns:
            list[QuoteItemModelDTO]: DTO list.
        """
        return [cls.build(instance) for instance in instances]
