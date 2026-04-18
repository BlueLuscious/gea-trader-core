""" MailHog-backed integration tests for the project mail service. """

from uuid import uuid4
from core.mail import MailMessageDTO, MailRecipientDTO, MailService
from core.tests.mail.integration.base import BaseMailIntegrationSimpleTestCase


class TestMailhogMailServiceIntegration(BaseMailIntegrationSimpleTestCase):
    """ Verify the project mail service can send real SMTP mail to MailHog. """

    def test_send_delivers_one_real_message_to_mailhog(self) -> None:
        """ Deliver one real SMTP message and confirm MailHog captures it. """
        subject = f"MailHog single integration {uuid4()}"
        message = self.build_unique_message(subject=subject, body="Single integration body")

        delivered_count = MailService.send(message)

        self.assertEqual(1, delivered_count)
        self.assertTrue(self.mailhog_contains_subject(subject))

    def test_send_many_delivers_multiple_real_messages_to_mailhog(self) -> None:
        """ Deliver multiple real SMTP messages and confirm MailHog captures each one. """
        first_subject = f"MailHog batch first {uuid4()}"
        second_subject = f"MailHog batch second {uuid4()}"

        first_message = self.build_unique_message(subject=first_subject, body="First integration body")
        second_message = MailMessageDTO(
            subject=second_subject,
            to=[MailRecipientDTO(email="integration@example.com")],
            text_body="Second integration body",
        )

        delivered_count = MailService.send_many([first_message, second_message])

        self.assertEqual(2, delivered_count)
        self.assertEqual(1, self.mailhog_subject_count(first_subject))
        self.assertEqual(1, self.mailhog_subject_count(second_subject))
