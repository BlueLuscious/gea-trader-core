""" Tests for the templated mail request payload serializer. """

from uuid import uuid4
from core.mail import (
    MailRecipientDTO,
    TemplateMailRequestDTO,
    TemplateMailRequestPayloadSerializer,
)
from core.testing import LoggedTestCase
from tenancy.models import TenantModel


class TestTemplateMailRequestPayloadSerializer(LoggedTestCase):
    """ Verify templated mail requests can be serialized for Celery transport. """

    def test_roundtrip_preserves_templates_context_and_tenant_snapshot(self) -> None:
        """ Serialize and deserialize one templated mail request while snapshotting one explicit tenant context. """
        tenant = TenantModel.objects.create(
            name="GEA Trader",
            slug=f"gea-trader-{uuid4()}",
            business_email="hello@gea-trader.test",
        )
        request = TemplateMailRequestDTO(
            subject="Serializer test",
            to=[MailRecipientDTO(email="owner@example.com", name="Owner User")],
            context={"mail_title": "Serializer test", "mail_body": "Template body"},
            html_template_name="mail/messages/test_message.html",
            text_template_name="mail/messages/test_message.txt",
            tenant=tenant,
            reply_to=["reply@example.com"],
        )

        payload = TemplateMailRequestPayloadSerializer.serialize(request)
        rebuilt_request = TemplateMailRequestPayloadSerializer.deserialize(payload)

        self.assertEqual(request.subject, rebuilt_request.subject)
        self.assertEqual(request.html_template_name, rebuilt_request.html_template_name)
        self.assertIsNone(rebuilt_request.tenant)
        self.assertEqual("GEA Trader", rebuilt_request.context["product_name"])
        self.assertIsNone(rebuilt_request.context["product_logo_url"])
        self.assertEqual("hello@gea-trader.test", rebuilt_request.context["support_email"])
        self.assertEqual("Serializer test", rebuilt_request.context["mail_title"])
        self.assertEqual(request.reply_to, rebuilt_request.reply_to)

    def test_serialize_allows_one_unpersisted_tenant_by_snapshotting_its_context(self) -> None:
        """ Serialize one async templated payload by snapshotting one explicit tenant even when it is not persisted. """
        request = TemplateMailRequestDTO(
            subject="Serializer test",
            to=[MailRecipientDTO(email="owner@example.com", name="Owner User")],
            context={"mail_title": "Serializer test", "mail_body": "Template body"},
            html_template_name="mail/messages/test_message.html",
            text_template_name="mail/messages/test_message.txt",
            tenant=TenantModel(name="GEA Trader", slug="gea-trader"),
        )

        payload = TemplateMailRequestPayloadSerializer.serialize(request)

        self.assertEqual("GEA Trader", payload["context"]["product_name"])
        self.assertIsNone(payload["context"]["product_logo_url"])
        self.assertNotIn("tenant_id", payload)
