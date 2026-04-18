""" MailHog-backed asynchronous integration tests for the templated mail service. """

from uuid import uuid4
from core.mail import MailRecipientDTO, TemplateMailRequestDTO, TemplateMailService
from core.tests.mail.integration.base import BaseAsyncMailIntegrationTransactionTestCase
from tenancy.models import TenantBrandingModel, TenantModel


class TestMailhogAsyncTemplateMailServiceIntegration(BaseAsyncMailIntegrationTransactionTestCase):
    """ Verify asynchronous templated mail delivery reaches MailHog through Celery. """

    def test_send_async_delivers_one_real_templated_message_to_mailhog(self) -> None:
        """ Deliver one templated mail message asynchronously and confirm MailHog captures it. """
        subject = f"MailHog async templated {uuid4()}"

        async_result = TemplateMailService.send_async(
            TemplateMailRequestDTO(
                subject=subject,
                to=[MailRecipientDTO(email="integration@example.com", name="Integration User")],
                context={
                    "mail_title": "Async integration template",
                    "mail_intro": "Hello from the asynchronous templated integration flow.",
                    "mail_body": "This message should appear in MailHog after Celery processing.",
                    "mail_outro": "Regards from the async template service.",
                },
                html_template_name="mail/messages/test_message.html",
                text_template_name="mail/messages/test_message.txt",
            ),
        )
        delivered_count = async_result.get(timeout=self.mailhog_wait_timeout_seconds)

        self.assertEqual(1, delivered_count)
        self.wait_for_mailhog_subject(subject)

    def test_send_async_delivers_one_real_tenant_aware_templated_message_to_mailhog(self) -> None:
        """ Deliver one tenant-aware templated message asynchronously and confirm MailHog captures its business context. """
        subject = f"MailHog async tenant aware {uuid4()}"
        tenant = TenantModel.objects.create(
            name="GEA Trader Legal",
            slug=f"gea-trader-legal-{uuid4()}",
            support_email="support@gea-trader.test",
            phone_number="+54 11 5555 1234",
            website_url="https://gea-trader.test",
        )
        TenantBrandingModel.objects.create(
            tenant=tenant,
            display_name="GEA Trader",
        )

        async_result = TemplateMailService.send_async(
            TemplateMailRequestDTO(
                subject=subject,
                to=[MailRecipientDTO(email="integration@example.com", name="Integration User")],
                context={
                    "mail_title": "Async tenant integration",
                    "mail_body": "This tenant-aware async message should appear in MailHog.",
                },
                html_template_name="mail/messages/test_message.html",
                text_template_name="mail/messages/test_message.txt",
                tenant=tenant,
            ),
        )
        delivered_count = async_result.get(timeout=self.mailhog_wait_timeout_seconds)

        self.assertEqual(1, delivered_count)
        self.wait_for_mailhog_subject(subject)
        self.wait_for_mailhog_text("GEA Trader")
        self.wait_for_mailhog_text("support@gea-trader.test")
