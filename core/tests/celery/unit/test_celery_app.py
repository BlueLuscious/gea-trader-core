""" Tests for the project-level Celery application wiring. """

from django.conf import settings
from core.celery import celery_app
from core.testing import LoggedSimpleTestCase


class TestCeleryApp(LoggedSimpleTestCase):
    """ Verify the project Celery application loads the expected configuration. """

    def test_celery_app_uses_the_project_name_and_broker_settings(self) -> None:
        """ Verify the Celery app is configured from Django settings with the expected broker values. """
        self.assertEqual("core", celery_app.main)
        self.assertEqual(settings.CELERY_BROKER_URL, celery_app.conf.broker_url)
        self.assertEqual(settings.CELERY_RESULT_BACKEND, celery_app.conf.result_backend)
        self.assertTrue(celery_app.conf.broker_connection_retry_on_startup)
        for schedule_name, schedule_entry in settings.CELERY_BEAT_SCHEDULE.items():
            self.assertEqual(schedule_entry, celery_app.conf.beat_schedule[schedule_name])

    def test_celery_app_registers_the_shared_mail_tasks(self) -> None:
        """ Verify the Celery app registers discovered project task modules. """
        celery_app.autodiscover_tasks(force=True)

        self.assertIn("core.tasks.mail.send_mail_message_task", celery_app.tasks)
        self.assertIn("core.tasks.mail.send_templated_mail_task", celery_app.tasks)

    def test_celery_app_autodiscovers_schedule_packages(self) -> None:
        """ Verify the Celery app imports installed app schedule packages. """
        celery_app.autodiscover_tasks(related_name="schedules", force=True)

        self.assertIn("core.schedules", celery_app.loader.task_modules)
        self.assertIn("cart.schedules", celery_app.loader.task_modules)
