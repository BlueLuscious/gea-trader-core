""" Cart-owned Celery Beat schedule registration. """

from celery import Celery
from core.celery import celery_app
from cart.schedules.lifecycle import (
    CLOSE_EXPIRED_CARTS_EVERY_SECONDS,
    CLOSE_EXPIRED_CARTS_SCHEDULE_NAME,
    register_lifecycle_schedules,
)


def register_schedules(app: Celery) -> None:
    """ Register cart-owned periodic task schedules.

    Args:
        app: Celery application receiving periodic task entries.
    """
    register_lifecycle_schedules(app)


@celery_app.on_after_finalize.connect
def register_cart_schedules(sender: Celery, **kwargs: object) -> None:
    """ Register cart schedules once Celery finishes task discovery.

    Args:
        sender: Celery application that emitted the finalization signal.
        **kwargs: Additional signal payload from Celery.
    """
    register_schedules(sender)


__all__: list[str] = [
    "CLOSE_EXPIRED_CARTS_EVERY_SECONDS",
    "CLOSE_EXPIRED_CARTS_SCHEDULE_NAME",
    "register_cart_schedules",
    "register_schedules",
]
