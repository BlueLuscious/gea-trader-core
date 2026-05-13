""" Tests for cart quote-request notification dispatching. """

from django.core import mail
from django.test import override_settings
from core.testing.base import LoggedTestCase
from quotation.models import QuoteModel
from quotation.services import CartQuoteRequestNotificationDispatcher
from tenancy.models import TenantModel


class TestCartQuoteRequestNotificationDispatcher(LoggedTestCase):
    """ Verify notification recipient resolution and dispatch behavior. """

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
        BASE_URL="https://owner.geatrader.test",
    )
    def test_send_dispatches_notification_when_tenant_has_contact_email(self) -> None:
        """ Verify a tenant contact email receives one quote notification. """
        tenant = TenantModel.objects.create(
            name="GEA Oils",
            slug="gea-oils-dispatcher",
            business_email="info@geaoils.test",
            is_active=True,
        )
        quote = QuoteModel.objects.create(
            tenant=tenant,
            customer_name="Ada Lovelace",
            customer_email="ada@example.com",
        )

        task_id = CartQuoteRequestNotificationDispatcher.send(quote=quote)

        self.assertTrue(task_id)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Ada Lovelace", mail.outbox[0].subject)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_send_skips_notification_when_tenant_has_no_contact_email(self) -> None:
        """ Verify missing tenant recipient leaves notification unsent. """
        tenant = TenantModel.objects.create(
            name="GEA Oils",
            slug="gea-oils-dispatcher-empty",
            is_active=True,
        )
        quote = QuoteModel.objects.create(tenant=tenant, customer_name="Ada Lovelace")

        task_id = CartQuoteRequestNotificationDispatcher.send(quote=quote)

        self.assertIsNone(task_id)
        self.assertEqual(len(mail.outbox), 0)
