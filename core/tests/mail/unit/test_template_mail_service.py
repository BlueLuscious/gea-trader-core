""" Tests for the templated mail service. """

from django.core import mail
from django.test import override_settings
from unittest.mock import patch
from core.mail import MailRecipientDTO, TemplateMailRequestDTO, TemplateMailService
from core.testing import LoggedSimpleTestCase
from tenancy.models import TenantBrandingModel, TenantModel
from tenancy.runtime import ActiveTenantContext


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@example.com",
)
class TestTemplateMailService(LoggedSimpleTestCase):
    """ Verify templated mail is rendered and delivered through the mail service. """

    def setUp(self) -> None:
        """ Reset the in-memory outbox before each test.

        Returns:
            None
        """
        super().setUp()
        mail.outbox = []

    def test_send_delivers_one_rendered_template_message(self) -> None:
        """ Deliver one templated message through the configured backend. """
        with patch("core.mail.services.template_mail_service.logger.info") as logger_info_mock:
            delivered_count = TemplateMailService.send(
                TemplateMailRequestDTO(
                    subject="Template mail service",
                    to=[MailRecipientDTO(email="owner@example.com", name="Owner User")],
                    context={
                        "mail_title": "Template mail service",
                        "mail_intro": "Hello there.",
                        "mail_body": "This message comes from one Django template.",
                        "mail_outro": "See you soon.",
                        "cta_label": "Open dashboard",
                        "cta_url": "https://example.com/dashboard",
                    },
                    html_template_name="mail/messages/test_message.html",
                    text_template_name="mail/messages/test_message.txt",
                ),
            )

        self.assertEqual(1, delivered_count)
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual("Template mail service", mail.outbox[0].subject)
        self.assertIn("This message comes from one Django template.", mail.outbox[0].body)
        self.assertNotIn("Enviado desde", mail.outbox[0].body)
        self.assertEqual(1, len(mail.outbox[0].alternatives))
        self.assertIn("Open dashboard", mail.outbox[0].alternatives[0][0])
        logger_info_mock.assert_called_once()

    def test_send_includes_active_tenant_business_context_when_available(self) -> None:
        """ Deliver one templated message with tenant-aware branding and contact values. """
        tenant = TenantModel(
            name="GEA Trader Legal",
            slug="gea-trader-legal",
            support_email="support@gea-trader.test",
            phone_number="+54 11 5555 1234",
            website_url="https://gea-trader.test",
        )
        branding = TenantBrandingModel(
            tenant=tenant,
            display_name="GEA Trader",
        )
        tenant._state.fields_cache["branding"] = branding
        tenant_token = ActiveTenantContext.set(tenant)

        try:
            delivered_count = TemplateMailService.send(
                TemplateMailRequestDTO(
                    subject="Template mail service",
                    to=[MailRecipientDTO(email="owner@example.com", name="Owner User")],
                    context={
                        "mail_title": "Template mail service",
                        "mail_body": "This message comes from one Django template.",
                    },
                    html_template_name="mail/messages/test_message.html",
                    text_template_name="mail/messages/test_message.txt",
                ),
            )
        finally:
            ActiveTenantContext.reset(tenant_token)

        self.assertEqual(1, delivered_count)
        self.assertEqual(1, len(mail.outbox))
        self.assertIn("Enviado desde GEA Trader", mail.outbox[0].body)
        self.assertIn("Soporte: support@gea-trader.test", mail.outbox[0].body)
        self.assertIn("Teléfono: +54 11 5555 1234", mail.outbox[0].body)
        self.assertIn("Sitio web: https://gea-trader.test", mail.outbox[0].body)

    def test_send_accepts_an_explicit_tenant_without_relying_on_runtime_context(self) -> None:
        """ Deliver one templated message using an explicit tenant snapshot instead of ambient runtime state. """
        tenant = TenantModel(
            name="GEA Trader Legal",
            slug="gea-trader-legal",
            business_email="hello@gea-trader.test",
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
                subject="Template mail service",
                to=[MailRecipientDTO(email="owner@example.com", name="Owner User")],
                context={
                    "mail_title": "Template mail service",
                    "mail_body": "This message comes from one Django template.",
                },
                html_template_name="mail/messages/test_message.html",
                text_template_name="mail/messages/test_message.txt",
                tenant=tenant,
            ),
        )

        self.assertEqual(1, delivered_count)
        self.assertEqual(1, len(mail.outbox))
        self.assertIn("Enviado desde GEA Trader", mail.outbox[0].body)
        self.assertIn("Soporte: hello@gea-trader.test", mail.outbox[0].body)
        self.assertIn("Teléfono: +54 11 5555 1234", mail.outbox[0].body)
        self.assertIn("Sitio web: https://gea-trader.test", mail.outbox[0].body)
