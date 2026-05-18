""" MailHog-backed integration tests for the templated mail service. """

from uuid import uuid4
from core.mail import MailRecipientDTO, TemplateMailRequestDTO, TemplateMailService
from core.tests.mail.integration.base import BaseMailIntegrationSimpleTestCase
from tenancy.models import TenantBrandingModel, TenantModel


class TestMailhogTemplateMailServiceIntegration(BaseMailIntegrationSimpleTestCase):
    """ Verify the templated mail service can send real SMTP mail to MailHog. """

    def test_send_delivers_one_real_templated_message_to_mailhog(self) -> None:
        """ Deliver one real templated message and confirm MailHog captures it. """
        subject = f"MailHog templated single {uuid4()}"

        delivered_count = TemplateMailService.send(
            TemplateMailRequestDTO(
                subject=subject,
                to=[MailRecipientDTO(email="integration@example.com", name="Integration User")],
                context={
                    "mail_title": "Integration template",
                    "mail_intro": "Hello from the templated integration flow.",
                    "mail_body": "This message should appear in MailHog.",
                    "mail_outro": "Regards from the template service.",
                    "cta_label": "Open dashboard",
                    "cta_url": "https://example.com/dashboard",
                },
                html_template_name="core/mail/messages/test_message.html",
                text_template_name="core/mail/messages/test_message.txt",
            ),
        )

        self.assertEqual(1, delivered_count)
        self.assertTrue(self.mailhog_contains_subject(subject))

    def test_send_delivers_multiple_real_templated_messages_to_mailhog(self) -> None:
        """ Deliver multiple templated messages and confirm MailHog captures both subjects. """
        first_subject = f"MailHog templated first {uuid4()}"
        second_subject = f"MailHog templated second {uuid4()}"

        first_delivered_count = TemplateMailService.send(
            TemplateMailRequestDTO(
                subject=first_subject,
                to=[MailRecipientDTO(email="integration@example.com")],
                context={
                    "mail_title": "First templated integration",
                    "mail_body": "First templated body.",
                },
                html_template_name="core/mail/messages/test_message.html",
                text_template_name="core/mail/messages/test_message.txt",
            ),
        )
        second_delivered_count = TemplateMailService.send(
            TemplateMailRequestDTO(
                subject=second_subject,
                to=[MailRecipientDTO(email="integration@example.com")],
                context={
                    "mail_title": "Second templated integration",
                    "mail_body": "Second templated body.",
                },
                html_template_name="core/mail/messages/test_message.html",
                text_template_name="core/mail/messages/test_message.txt",
            ),
        )

        self.assertEqual(1, first_delivered_count)
        self.assertEqual(1, second_delivered_count)
        self.assertEqual(1, self.mailhog_subject_count(first_subject))
        self.assertEqual(1, self.mailhog_subject_count(second_subject))

    def test_send_delivers_one_real_tenant_aware_templated_message_to_mailhog(self) -> None:
        """ Deliver one real templated message using an explicit tenant context and confirm MailHog captures its tenant-aware content. """
        subject = f"MailHog templated tenant aware {uuid4()}"
        tenant = TenantModel(
            name="GEA Trader Legal",
            slug=f"gea-trader-legal-{uuid4()}",
            support_email="support@gea-trader.test",
            phone_number="+54 11 5555 1234",
            website_url="https://gea-trader.test",
        )
        branding = TenantBrandingModel(
            tenant=tenant,
            display_name="GEA Trader",
        )
        tenant._state.fields_cache["branding"] = branding

        delivered_count = TemplateMailService.send(
            TemplateMailRequestDTO(
                subject=subject,
                to=[MailRecipientDTO(email="integration@example.com", name="Integration User")],
                context={
                    "mail_title": "Integration template",
                    "mail_body": "This tenant-aware message should appear in MailHog.",
                },
                html_template_name="core/mail/messages/test_message.html",
                text_template_name="core/mail/messages/test_message.txt",
                tenant=tenant,
            ),
        )

        self.assertEqual(1, delivered_count)
        self.assertTrue(self.mailhog_contains_subject(subject))
        self.assertTrue(self.mailhog_contains_text("GEA Trader"))
        self.assertTrue(self.mailhog_contains_text("support@gea-trader.test"))

    def test_send_delivers_multiple_real_tenant_aware_templated_messages_to_mailhog(self) -> None:
        """ Deliver multiple real templated messages with different explicit tenants and confirm MailHog captures both business contexts. """
        first_subject = f"MailHog tenant aware first {uuid4()}"
        second_subject = f"MailHog tenant aware second {uuid4()}"
        first_tenant = TenantModel(
            name="First Legal Business",
            slug=f"first-legal-business-{uuid4()}",
            business_email="hello@first-business.test",
        )
        second_tenant = TenantModel(
            name="Second Legal Business",
            slug=f"second-legal-business-{uuid4()}",
            support_email="support@second-business.test",
        )
        first_branding = TenantBrandingModel(
            tenant=first_tenant,
            display_name="First Business",
        )
        second_branding = TenantBrandingModel(
            tenant=second_tenant,
            display_name="Second Business",
        )
        first_tenant._state.fields_cache["branding"] = first_branding
        second_tenant._state.fields_cache["branding"] = second_branding

        first_delivered_count = TemplateMailService.send(
            TemplateMailRequestDTO(
                subject=first_subject,
                to=[MailRecipientDTO(email="integration@example.com")],
                context={
                    "mail_title": "First tenant-aware integration",
                    "mail_body": "First tenant-aware body.",
                },
                html_template_name="core/mail/messages/test_message.html",
                text_template_name="core/mail/messages/test_message.txt",
                tenant=first_tenant,
            ),
        )
        second_delivered_count = TemplateMailService.send(
            TemplateMailRequestDTO(
                subject=second_subject,
                to=[MailRecipientDTO(email="integration@example.com")],
                context={
                    "mail_title": "Second tenant-aware integration",
                    "mail_body": "Second tenant-aware body.",
                },
                html_template_name="core/mail/messages/test_message.html",
                text_template_name="core/mail/messages/test_message.txt",
                tenant=second_tenant,
            ),
        )

        self.assertEqual(1, first_delivered_count)
        self.assertEqual(1, second_delivered_count)
        self.assertEqual(1, self.mailhog_subject_count(first_subject))
        self.assertEqual(1, self.mailhog_subject_count(second_subject))
        self.assertTrue(self.mailhog_contains_text("First Business"))
        self.assertTrue(self.mailhog_contains_text("Second Business"))
