from collections.abc import Iterable
from quotation.dtos.quote_model_dto import QuoteModelDTO
from quotation.models import QuoteModel


class QuoteModelDTOFactory:
    """ Factory for transforming quote models into DTOs. """

    @staticmethod
    def build(instance: QuoteModel) -> QuoteModelDTO:
        """ Build a quote DTO.

        Args:
            instance: Quote model instance.

        Returns:
            QuoteModelDTO: Serialized quote.
        """
        return QuoteModelDTO(
            id=instance.id,
            tenant_id=str(instance.tenant_id),
            cart_id=instance.cart_id,
            user_id=instance.user_id,
            status=instance.status,
            customer_name=instance.customer_name,
            customer_email=instance.customer_email,
            customer_phone=instance.customer_phone,
            company_name=instance.company_name,
            tax_id=instance.tax_id,
            notes=instance.notes,
            requested_at=instance.requested_at,
            sent_at=instance.sent_at,
            answered_at=instance.answered_at,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

    @classmethod
    def build_many(cls, instances: Iterable[QuoteModel]) -> list[QuoteModelDTO]:
        """ Build multiple quote DTOs.

        Args:
            instances: Iterable of quote models.

        Returns:
            list[QuoteModelDTO]: DTO list.
        """
        return [cls.build(instance) for instance in instances]
