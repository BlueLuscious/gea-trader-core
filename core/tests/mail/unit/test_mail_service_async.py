""" Tests for asynchronous raw mail service dispatch. """

from unittest.mock import MagicMock, patch
from core.mail import MailMessageDTO, MailRecipientDTO, MailService
from core.testing import LoggedSimpleTestCase


class TestMailServiceAsync(LoggedSimpleTestCase):
    """ Verify raw mail services enqueue Celery tasks with serialized payloads. """

    def test_send_async_serializes_the_message_and_dispatches_the_raw_mail_task(self) -> None:
        """ Serialize one raw mail payload and enqueue the shared raw mail task. """
        message = MailMessageDTO(
            subject="Async test",
            to=[MailRecipientDTO(email="owner@example.com", name="Owner User")],
            text_body="Plain body",
            html_body="<p>Plain body</p>",
        )
        async_result = MagicMock()
        async_result.id = "task-123"

        with (
            patch("core.tasks.mail.tasks.send_mail_message_task.delay", return_value=async_result) as delay_mock,
            patch("core.mail.services.mail_service.logger.info") as logger_info_mock,
        ):
            returned_result = MailService.send_async(message, fail_silently=True)

        self.assertIs(async_result, returned_result)
        self.assertEqual("Async test", delay_mock.call_args.kwargs["payload"]["subject"])
        self.assertTrue(delay_mock.call_args.kwargs["fail_silently"])
        logger_info_mock.assert_called_once()
