""" Tests for the templated mail composer. """

from core.mail import MailRecipientDTO, TemplateMailComposer, TemplateMailRequestDTO
from core.testing import LoggedSimpleTestCase
from tenancy.models import TenantBrandingModel, TenantModel
from tenancy.runtime import ActiveTenantContext


class TestTemplateMailComposer(LoggedSimpleTestCase):
    """ Verify templated mail requests compose into outbound mail DTOs. """

    def test_compose_builds_one_rendered_mail_message(self) -> None:
        """ Compose one templated request into one mail message DTO. """
        message = TemplateMailComposer.compose(
            TemplateMailRequestDTO(
                subject="Template composer",
                to=[MailRecipientDTO(email="owner@example.com", name="Owner User")],
                context={
                    "mail_title": "Template composer",
                    "mail_body": "This message comes from one composer.",
                },
                html_template_name="core/mail/messages/test_message.html",
                text_template_name="core/mail/messages/test_message.txt",
            ),
        )

        self.assertEqual("Template composer", message.subject)
        self.assertIn("This message comes from one composer.", message.text_body)
        self.assertIsNone(message.from_email)

    def test_compose_uses_an_explicit_tenant_without_leaking_runtime_context(self) -> None:
        """ Compose one templated request using one explicit tenant and restore runtime context afterwards. """
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

        message = TemplateMailComposer.compose(
            TemplateMailRequestDTO(
                subject="Template composer",
                to=[MailRecipientDTO(email="owner@example.com", name="Owner User")],
                context={
                    "mail_title": "Template composer",
                    "mail_body": "This message comes from one composer.",
                },
                html_template_name="core/mail/messages/test_message.html",
                text_template_name="core/mail/messages/test_message.txt",
                tenant=tenant,
            ),
        )

        self.assertIn("Enviado desde GEA Trader", message.text_body)
        self.assertIn("Soporte: hello@gea-trader.test", message.text_body)
        self.assertIsNone(ActiveTenantContext.get())
