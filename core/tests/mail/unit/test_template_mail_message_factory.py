""" Tests for the templated mail message factory. """

from core.mail import MailRecipientDTO, TemplateMailRequestDTO
from core.mail.factories import TemplateMailMessageFactory
from core.testing import LoggedSimpleTestCase
from tenancy.models import TenantBrandingModel, TenantModel
from tenancy.runtime import ActiveTenantContext


class TestTemplateMailMessageFactory(LoggedSimpleTestCase):
    """ Verify one template pair is converted into one outbound mail DTO. """

    def test_build_renders_text_html_and_keeps_routing_metadata(self) -> None:
        """ Build one outbound DTO preserving rendered bodies and reply metadata. """
        message = TemplateMailMessageFactory.build(
            request=TemplateMailRequestDTO(
                subject="Template factory",
                to=[MailRecipientDTO(email="owner@example.com")],
                context={
                    "mail_title": "Template factory",
                    "mail_body": "Factory body",
                    "cta_label": "Open dashboard",
                    "cta_url": "https://example.com/dashboard",
                },
                html_template_name="mail/messages/test_message.html",
                text_template_name="mail/messages/test_message.txt",
                reply_to=["reply@example.com"],
                headers={"X-Test": "factory"},
            ),
        )

        self.assertEqual("Template factory", message.subject)
        self.assertIn("Factory body", message.text_body)
        self.assertIn("Factory body", str(message.html_body))
        self.assertNotIn("Sent via", message.text_body)
        self.assertNotIn("Sent via", str(message.html_body))
        self.assertEqual(("reply@example.com",), message.reply_to)
        self.assertEqual({"X-Test": "factory"}, message.headers)

    def test_build_uses_active_tenant_context_when_no_explicit_branding_values_exist(self) -> None:
        """ Build one outbound DTO using the active tenant mail context as the base layer. """
        tenant = TenantModel(
            name="GEA Trader",
            slug="gea-trader",
            business_email="hello@gea-trader.test",
            phone_number="+54 11 5555 9999",
            website_url="https://gea-trader.test",
        )
        branding = TenantBrandingModel(
            tenant=tenant,
            display_name="GEA Trader Pro",
        )
        tenant._state.fields_cache["branding"] = branding
        tenant_token = ActiveTenantContext.set(tenant)

        try:
            message = TemplateMailMessageFactory.build(
                request=TemplateMailRequestDTO(
                    subject="Template factory",
                    to=[MailRecipientDTO(email="owner@example.com")],
                    context={
                        "mail_title": "Template factory",
                        "mail_body": "Factory body",
                    },
                    html_template_name="mail/messages/test_message.html",
                    text_template_name="mail/messages/test_message.txt",
                ),
            )
        finally:
            ActiveTenantContext.reset(tenant_token)

        self.assertIn("Sent via GEA Trader Pro", message.text_body)
        self.assertIn("Support: hello@gea-trader.test", message.text_body)
        self.assertIn("Phone: +54 11 5555 9999", message.text_body)
        self.assertIn("Website: https://gea-trader.test", message.text_body)
