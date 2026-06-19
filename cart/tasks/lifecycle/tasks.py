""" Celery tasks for cart lifecycle maintenance. """

import logging
from celery import shared_task
from cart.services import CartExpirationService

logger = logging.getLogger(__name__)


@shared_task(name="cart.tasks.lifecycle.close_expired_carts_task")
def close_expired_carts_task() -> int:
    """ Close carts whose expiration timestamp has already passed.

    Returns:
        int: Number of carts closed.
    """
    closed_count = CartExpirationService.close_expired_carts()
    logger.info("Closed expired carts count=%s", closed_count)
    return closed_count
