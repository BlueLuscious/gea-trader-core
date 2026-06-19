""" Celery Beat schedules for cart lifecycle maintenance. """

from celery import Celery
from cart.settings import CLOSE_EXPIRED_CARTS_EVERY_SECONDS
from cart.tasks import close_expired_carts_task

CLOSE_EXPIRED_CARTS_SCHEDULE_NAME = "cart.close_expired_carts"


def register_lifecycle_schedules(app: Celery) -> None:
    """ Register cart lifecycle periodic tasks.

    Args:
        app: Celery application receiving periodic task entries.
    """
    app.add_periodic_task(
        CLOSE_EXPIRED_CARTS_EVERY_SECONDS,
        close_expired_carts_task.s(),
        name=CLOSE_EXPIRED_CARTS_SCHEDULE_NAME,
    )


__all__: list[str] = [
    "CLOSE_EXPIRED_CARTS_EVERY_SECONDS",
    "CLOSE_EXPIRED_CARTS_SCHEDULE_NAME",
    "register_lifecycle_schedules",
]
