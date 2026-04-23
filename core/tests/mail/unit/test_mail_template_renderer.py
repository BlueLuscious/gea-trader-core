""" Tests for the mail template renderer. """

from core.mail.renderers import MailTemplateRenderer
from core.testing import LoggedSimpleTestCase
from tenancy.models import TenantBrandingModel, TenantModel
from tenancy.runtime import ActiveTenantContext


class TestMailTemplateRenderer(LoggedSimpleTestCase):
    """ Verify mail templates render with the expected base context. """

    def test_render_text_keeps_the_output_neutral_when_no_branding_context_exists(self) -> None:
        """ Render the text template without inventing product or support branding. """
        rendered_text = MailTemplateRenderer.render_text(
            "mail/messages/test_message.txt",
            {
                "mail_title": "Renderer test",
                "mail_body": "Plain text body",
            },
        )

        self.assertIn("Renderer test", rendered_text)
        self.assertIn("Plain text body", rendered_text)
        self.assertNotIn("Enviado desde", rendered_text)
        self.assertNotIn("Soporte:", rendered_text)
        self.assertNotIn("---", rendered_text)

    def test_render_html_keeps_the_output_neutral_when_no_branding_context_exists(self) -> None:
        """ Render the HTML template without inventing product or support branding. """
        rendered_html = MailTemplateRenderer.render_html(
            "mail/messages/test_message.html",
            {
                "mail_title": "Renderer test",
                "mail_body": "HTML body",
            },
        )

        self.assertIn("Renderer test", rendered_html)
        self.assertIn("HTML body", rendered_html)
        self.assertNotIn("Enviado desde", rendered_html)
        self.assertNotIn("Soporte:", rendered_html)
        self.assertNotIn("Teléfono:", rendered_html)
        self.assertNotIn("Sitio web:", rendered_html)
        self.assertNotIn("border-top:1px solid #d9e0eb", rendered_html)

    def test_render_html_includes_branding_when_context_provides_it(self) -> None:
        """ Render the HTML template with explicit product and support branding context. """
        rendered_html = MailTemplateRenderer.render_html(
            "mail/messages/test_message.html",
            {
                "mail_title": "Renderer test",
                "mail_body": "HTML body",
                "product_name": "Northwind Traders",
                "support_email": "support@northwind.test",
            },
        )

        self.assertIn("Northwind Traders", rendered_html)
        self.assertIn("support@northwind.test", rendered_html)

    def test_render_text_includes_active_tenant_business_context(self) -> None:
        """ Render the text template using the active tenant context when the caller does not override it. """
        tenant = TenantModel(
            name="GEA Trader Legal",
            slug="gea-trader-legal",
            business_email="hello@gea-trader.test",
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
            rendered_text = MailTemplateRenderer.render_text(
                "mail/messages/test_message.txt",
                {
                    "mail_title": "Renderer test",
                    "mail_body": "Plain text body",
                },
            )
        finally:
            ActiveTenantContext.reset(tenant_token)

        self.assertIn("Enviado desde GEA Trader", rendered_text)
        self.assertIn("Soporte: support@gea-trader.test", rendered_text)
        self.assertIn("Teléfono: +54 11 5555 1234", rendered_text)
        self.assertIn("Sitio web: https://gea-trader.test", rendered_text)

    def test_render_html_allows_explicit_context_to_override_active_tenant_values(self) -> None:
        """ Render the HTML template with explicit values taking precedence over the active tenant context. """
        tenant = TenantModel(
            name="GEA Trader Legal",
            slug="gea-trader-legal",
            support_email="support@gea-trader.test",
        )
        branding = TenantBrandingModel(
            tenant=tenant,
            display_name="GEA Trader",
        )
        tenant._state.fields_cache["branding"] = branding
        tenant_token = ActiveTenantContext.set(tenant)

        try:
            rendered_html = MailTemplateRenderer.render_html(
                "mail/messages/test_message.html",
                {
                    "mail_title": "Renderer test",
                    "mail_body": "HTML body",
                    "product_name": "Override Brand",
                    "support_email": "override@example.com",
                },
            )
        finally:
            ActiveTenantContext.reset(tenant_token)

        self.assertIn("Override Brand", rendered_html)
        self.assertIn("override@example.com", rendered_html)
        self.assertNotIn("support@gea-trader.test", rendered_html)
