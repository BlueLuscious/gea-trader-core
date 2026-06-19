""" Tests for cart lifecycle schedule registration. """

from dataclasses import dataclass
from typing import cast
from celery import Celery
from celery.canvas import Signature
from core.testing.base import LoggedSimpleTestCase
from cart.schedules import register_schedules
from cart.schedules.lifecycle import (
    CLOSE_EXPIRED_CARTS_EVERY_SECONDS,
    CLOSE_EXPIRED_CARTS_SCHEDULE_NAME,
)


@dataclass(frozen=True)
class PeriodicTaskRegistration:
    """ Captured periodic task registration for schedule tests. """

    schedule: int
    signature: Signature
    name: str


class RecordingCeleryApp:
    """ Minimal Celery app test double that records periodic task registrations. """

    def __init__(self) -> None:
        """ Initialize an empty registration list. """
        self.registrations: list[PeriodicTaskRegistration] = []

    def add_periodic_task(self, schedule: int, sig: Signature, name: str) -> None:
        """ Record a periodic task registration.

        Args:
            schedule: Schedule interval in seconds.
            sig: Celery task signature.
            name: Stable schedule entry name.
        """
        self.registrations.append(
            PeriodicTaskRegistration(
                schedule=schedule,
                signature=sig,
                name=name,
            )
        )


class TestCartLifecycleSchedules(LoggedSimpleTestCase):
    """ Verify cart lifecycle schedule registration. """

    def test_register_schedules_adds_close_expired_carts_periodic_task(self) -> None:
        """ Verify cart schedule registration adds the expired-cart closure task. """
        app = RecordingCeleryApp()

        register_schedules(cast(Celery, app))

        self.assertEqual(1, len(app.registrations))
        registration = app.registrations[0]
        self.assertEqual(CLOSE_EXPIRED_CARTS_EVERY_SECONDS, registration.schedule)
        self.assertEqual(CLOSE_EXPIRED_CARTS_SCHEDULE_NAME, registration.name)
        self.assertEqual("cart.tasks.lifecycle.close_expired_carts_task", registration.signature["task"])
