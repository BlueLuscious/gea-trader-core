""" Tests for the project mail service. """

from django.core import mail
from django.test import override_settings
from unittest.mock import patch
from core.mail import MailMessageDTO, MailRecipientDTO, MailService
from core.testing import LoggedSimpleTestCase


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@example.com",
)
class TestMailService(LoggedSimpleTestCase):
    """ Verify the project mail service sends outbound messages through Django. """

    def setUp(self) -> None:
        """ Reset the local in-memory outbox before each test.

        Returns:
            None
        """
        super().setUp()
        mail.outbox = []

    def test_send_delivers_one_message_through_the_configured_backend(self) -> None:
        """ Deliver one outbound message with plain and HTML bodies. """
        message = MailMessageDTO(
            subject="Single message",
            to=[MailRecipientDTO(email="owner@example.com", name="Owner User")],
            text_body="Plain body",
            html_body="<p>HTML body</p>",
        )

        with patch("core.mail.services.mail_service.logger.info") as logger_info_mock:
            delivered_count = MailService.send(message)

        self.assertEqual(1, delivered_count)
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual("Single message", mail.outbox[0].subject)
        self.assertEqual(["Owner User <owner@example.com>"], mail.outbox[0].to)
        self.assertEqual([("<p>HTML body</p>", "text/html")], mail.outbox[0].alternatives)
        logger_info_mock.assert_called_once()

    def test_send_many_reuses_one_backend_connection_for_multiple_messages(self) -> None:
        """ Deliver multiple outbound messages through one shared service call. """
        first_message = MailMessageDTO(
            subject="First message",
            to=[MailRecipientDTO(email="first@example.com")],
            text_body="First body",
        )
        second_message = MailMessageDTO(
            subject="Second message",
            to=[MailRecipientDTO(email="second@example.com")],
            text_body="Second body",
        )

        with patch("core.mail.services.mail_service.logger.info") as logger_info_mock:
            delivered_count = MailService.send_many([first_message, second_message])

        self.assertEqual(2, delivered_count)
        self.assertEqual(2, len(mail.outbox))
        self.assertEqual(["first@example.com"], mail.outbox[0].to)
        self.assertEqual(["second@example.com"], mail.outbox[1].to)
        logger_info_mock.assert_called_once()

    def test_send_many_returns_zero_when_the_message_list_is_empty(self) -> None:
        """ Return zero instead of opening one backend flow for an empty batch. """
        delivered_count = MailService.send_many([])

        self.assertEqual(0, delivered_count)
        self.assertEqual([], mail.outbox)
