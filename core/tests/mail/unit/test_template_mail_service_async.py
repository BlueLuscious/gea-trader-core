""" Tests for asynchronous templated mail service dispatch. """

from unittest.mock import MagicMock, patch
from uuid import uuid4
from core.mail import MailRecipientDTO, TemplateMailRequestDTO, TemplateMailService
from core.testing import LoggedTestCase
from tenancy.models import TenantModel


class TestTemplateMailServiceAsync(LoggedTestCase):
    """ Verify templated mail services enqueue Celery tasks with serialized payloads. """

    def test_send_async_serializes_the_request_and_dispatches_the_templated_mail_task(self) -> None:
        """ Serialize one templated mail request and enqueue the shared templated mail task. """
        tenant = TenantModel.objects.create(name="GEA Trader", slug=f"gea-trader-{uuid4()}")
        request = TemplateMailRequestDTO(
            subject="Async test",
            to=[MailRecipientDTO(email="owner@example.com", name="Owner User")],
            context={"mail_title": "Async test", "mail_body": "Template body"},
            html_template_name="core/mail/messages/test_message.html",
            text_template_name="core/mail/messages/test_message.txt",
            tenant=tenant,
        )
        async_result = MagicMock()
        async_result.id = "task-456"

        with (
            patch("core.tasks.mail.tasks.send_templated_mail_task.delay", return_value=async_result) as delay_mock,
            patch("core.mail.services.template_mail_service.logger.info") as logger_info_mock,
        ):
            returned_result = TemplateMailService.send_async(request, fail_silently=True)

        self.assertIs(async_result, returned_result)
        self.assertEqual("Async test", delay_mock.call_args.kwargs["payload"]["subject"])
        self.assertEqual("GEA Trader", delay_mock.call_args.kwargs["payload"]["context"]["product_name"])
        self.assertNotIn("tenant_id", delay_mock.call_args.kwargs["payload"])
        self.assertTrue(delay_mock.call_args.kwargs["fail_silently"])
        logger_info_mock.assert_called_once()
