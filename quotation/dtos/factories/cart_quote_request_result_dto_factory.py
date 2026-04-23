""" Factory helpers for building cart quote-request result DTOs. """

from typing import Optional
from quotation.dtos.cart_quote_request_result_dto import CartQuoteRequestResultDTO
from quotation.dtos.factories.quote_model_dto_factory import QuoteModelDTOFactory
from quotation.models import QuoteModel


class CartQuoteRequestResultDTOFactory:
    """ Factory for assembling cart quote-request result DTOs. """

    @staticmethod
    def build(*, quote: QuoteModel, notification_task_id: Optional[str]) -> CartQuoteRequestResultDTO:
        """ Build one cart quote-request result DTO.

        Args:
            quote: Persisted quote model created from the cart.
            notification_task_id: Celery task identifier for the notification mail.

        Returns:
            CartQuoteRequestResultDTO: Serialized service result.
        """
        return CartQuoteRequestResultDTO(
            quote=QuoteModelDTOFactory.build(quote),
            notification_task_id=notification_task_id,
        )
