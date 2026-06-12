""" Tests for the project-level Celery Beat schedule builder. """

from core.beat import CeleryBeatScheduleBuilder
from core.testing import LoggedSimpleTestCase


class TestCeleryBeatScheduleBuilder(LoggedSimpleTestCase):
    """ Verify the base Celery Beat schedule builder contract. """

    def test_build_returns_an_empty_schedule_until_periodic_tasks_are_registered(self) -> None:
        """ Verify the base Beat schedule starts empty before business schedules are added. """
        self.assertEqual({}, CeleryBeatScheduleBuilder.build())
