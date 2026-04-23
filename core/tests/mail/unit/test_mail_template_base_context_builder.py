""" Tests for the shared mail template base context builder. """

from core.mail.resolvers import MailTemplateBaseContextBuilder
from core.testing import LoggedSimpleTestCase
from tenancy.models import TenantBrandingModel, TenantModel
from tenancy.runtime import ActiveTenantContext


class TestMailTemplateBaseContextBuilder(LoggedSimpleTestCase):
    """ Verify the shared mail template base context builder stays consistent across sync and async flows. """

    def test_build_uses_the_active_tenant_context_when_no_explicit_tenant_is_provided(self) -> None:
        """ Build one mail base context from the active tenant when the caller does not pass an explicit tenant. """
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
            built_context = MailTemplateBaseContextBuilder.build(
                context={"mail_title": "Builder test", "mail_body": "Builder body"},
            )
        finally:
            ActiveTenantContext.reset(tenant_token)

        self.assertEqual("GEA Trader", built_context["product_name"])
        self.assertIsNone(built_context["product_logo_url"])
        self.assertEqual("support@gea-trader.test", built_context["support_email"])
        self.assertEqual("Builder test", built_context["mail_title"])

    def test_build_uses_one_explicit_tenant_snapshot_without_requiring_runtime_context(self) -> None:
        """ Build one mail base context from one explicit tenant snapshot without touching the ambient tenant context. """
        tenant = TenantModel(
            name="GEA Trader Legal",
            slug="gea-trader-legal",
            business_email="hello@gea-trader.test",
        )

        built_context = MailTemplateBaseContextBuilder.build(
            context={"mail_title": "Builder test", "mail_body": "Builder body"},
            tenant=tenant,
        )

        self.assertEqual("GEA Trader Legal", built_context["product_name"])
        self.assertIsNone(built_context["product_logo_url"])
        self.assertEqual("hello@gea-trader.test", built_context["support_email"])
        self.assertEqual("Builder test", built_context["mail_title"])

    def test_build_allows_caller_values_to_override_the_tenant_defaults(self) -> None:
        """ Build one mail base context with caller values taking precedence over tenant-derived defaults. """
        tenant = TenantModel(
            name="GEA Trader Legal",
            slug="gea-trader-legal",
            support_email="support@gea-trader.test",
        )

        built_context = MailTemplateBaseContextBuilder.build(
            context={
                "product_name": "Override Brand",
                "support_email": "override@example.com",
                "mail_title": "Builder test",
            },
            tenant=tenant,
        )

        self.assertEqual("Override Brand", built_context["product_name"])
        self.assertIsNone(built_context["product_logo_url"])
        self.assertEqual("override@example.com", built_context["support_email"])
