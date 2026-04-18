""" MailHog-backed asynchronous integration tests for the raw mail service. """

from uuid import uuid4
from core.mail import MailService
from core.tests.mail.integration.base import BaseAsyncMailIntegrationTransactionTestCase


class TestMailhogAsyncMailServiceIntegration(BaseAsyncMailIntegrationTransactionTestCase):
    """ Verify asynchronous raw mail delivery reaches MailHog through Celery. """

    def test_send_async_delivers_one_real_message_to_mailhog(self) -> None:
        """ Deliver one raw mail message asynchronously and confirm MailHog captures it. """
        subject = f"MailHog async single {uuid4()}"
        message = self.build_unique_message(subject=subject, body="Async integration body")

        async_result = MailService.send_async(message)
        delivered_count = async_result.get(timeout=self.mailhog_wait_timeout_seconds)

        self.assertEqual(1, delivered_count)
        self.wait_for_mailhog_subject(subject)
