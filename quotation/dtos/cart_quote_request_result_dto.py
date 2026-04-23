""" DTO that represents one completed public cart-to-quote request flow. """

from dataclasses import dataclass
from typing import Optional

from quotation.dtos.quote_model_dto import QuoteModelDTO


@dataclass(frozen=True)
class CartQuoteRequestResultDTO:
    """ Public DTO for one completed cart quote-request conversion.

    Args:
        quote: Serialized persisted quote root.
        notification_task_id: Celery task identifier for the enqueued notification mail.
    """

    quote: QuoteModelDTO
    notification_task_id: Optional[str] = None
