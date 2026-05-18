""" Tests for project-wide asynchronous mail tasks. """

from smtplib import SMTPException
from unittest.mock import patch
from uuid import uuid4
from core.tasks.mail.tasks import (
    MAIL_TASK_AUTORETRY_EXCEPTIONS,
    MAIL_TASK_MAX_RETRIES,
    MAIL_TASK_RETRY_BACKOFF_MAX_SECONDS,
    send_mail_message_task,
    send_templated_mail_task,
)
from core.testing import LoggedTestCase
from tenancy.models import TenantModel


class TestMailTasks(LoggedTestCase):
    """ Verify project-wide mail tasks rebuild payloads and delegate to mail services. """

    def test_mail_tasks_configure_retry_for_transient_transport_errors(self) -> None:
        """ Configure both mail tasks to retry transient transport failures with bounded backoff. """
        self.assertEqual(MAIL_TASK_AUTORETRY_EXCEPTIONS, send_mail_message_task.autoretry_for)
        self.assertEqual(MAIL_TASK_AUTORETRY_EXCEPTIONS, send_templated_mail_task.autoretry_for)
        self.assertEqual((SMTPException, TimeoutError, ConnectionError), MAIL_TASK_AUTORETRY_EXCEPTIONS)
        self.assertEqual(MAIL_TASK_MAX_RETRIES, send_mail_message_task.max_retries)
        self.assertEqual(MAIL_TASK_MAX_RETRIES, send_templated_mail_task.max_retries)
        self.assertTrue(send_mail_message_task.retry_backoff)
        self.assertTrue(send_templated_mail_task.retry_backoff)
        self.assertEqual(MAIL_TASK_RETRY_BACKOFF_MAX_SECONDS, send_mail_message_task.retry_backoff_max)
        self.assertEqual(MAIL_TASK_RETRY_BACKOFF_MAX_SECONDS, send_templated_mail_task.retry_backoff_max)
        self.assertTrue(send_mail_message_task.retry_jitter)
        self.assertTrue(send_templated_mail_task.retry_jitter)

    def test_send_mail_message_task_rebuilds_the_payload_and_delegates_to_the_mail_service(self) -> None:
        """ Rebuild one raw mail payload inside the task before delegating to the mail service. """
        with (
            patch("core.tasks.mail.tasks.MailService.send", return_value=1) as send_mock,
            patch("core.tasks.mail.tasks.logger.info") as logger_info_mock,
        ):
            delivered_count = send_mail_message_task(
                payload={
                    "subject": "Task test",
                    "to": [{"email": "owner@example.com", "name": "Owner User"}],
                    "text_body": "Plain body",
                    "html_body": "<p>Plain body</p>",
                    "from_email": None,
                    "cc": [],
                    "bcc": [],
                    "reply_to": [],
                    "headers": {},
                    "attachments": [],
                },
                fail_silently=True,
            )

        self.assertEqual(1, delivered_count)
        self.assertEqual("Task test", send_mock.call_args.args[0].subject)
        self.assertTrue(send_mock.call_args.kwargs["fail_silently"])
        logger_info_mock.assert_called_once()

    def test_send_templated_mail_task_rebuilds_the_payload_and_delegates_to_the_templated_service(self) -> None:
        """ Rebuild one templated mail payload inside the task before delegating to the templated mail service. """
        tenant = TenantModel.objects.create(
            name="GEA Trader",
            slug=f"gea-trader-{uuid4()}",
            business_email="hello@gea-trader.test",
        )

        with (
            patch("core.tasks.mail.tasks.TemplateMailService.send", return_value=1) as send_mock,
            patch("core.tasks.mail.tasks.logger.info") as logger_info_mock,
        ):
            delivered_count = send_templated_mail_task(
                payload={
                    "subject": "Task test",
                    "to": [{"email": "owner@example.com", "name": "Owner User"}],
                    "context": {
                        "product_name": "GEA Trader",
                        "support_email": "hello@gea-trader.test",
                        "mail_title": "Task test",
                        "mail_body": "Template body",
                    },
                    "html_template_name": "core/mail/messages/test_message.html",
                    "text_template_name": "core/mail/messages/test_message.txt",
                    "from_email": None,
                    "cc": [],
                    "bcc": [],
                    "reply_to": [],
                    "headers": {},
                    "attachments": [],
                },
                fail_silently=True,
            )

        self.assertEqual(1, delivered_count)
        self.assertEqual("Task test", send_mock.call_args.args[0].subject)
        self.assertIsNone(send_mock.call_args.args[0].tenant)
        self.assertEqual("GEA Trader", send_mock.call_args.args[0].context["product_name"])
        self.assertTrue(send_mock.call_args.kwargs["fail_silently"])
        logger_info_mock.assert_called_once()
