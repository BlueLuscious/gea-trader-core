""" Shared base cases for MailHog-backed mail integration tests. """

import os
from unittest import SkipTest
from django.conf import settings
from django.test import override_settings
from core.testing import LoggedSimpleTestCase, LoggedTransactionTestCase
from core.tests.mail.integration.mixins import MailIntegrationAssertionsMixin


def is_mail_integration_enabled() -> bool:
    """ Return whether mail integration tests should run.

    Returns:
        bool: True when mail integration tests are explicitly enabled.
    """
    return os.environ.get("RUN_MAIL_INTEGRATION_TESTS", "False").lower() in ("1", "true", "yes", "on")


def is_async_mail_integration_enabled() -> bool:
    """ Return whether asynchronous mail integration tests should run.

    Returns:
        bool: True when asynchronous mail integration tests are explicitly enabled.
    """
    return os.environ.get("RUN_ASYNC_MAIL_INTEGRATION_TESTS", "False").lower() in ("1", "true", "yes", "on")


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
    EMAIL_HOST="127.0.0.1",
    EMAIL_PORT=1025,
    DEFAULT_FROM_EMAIL="noreply@example.com",
)
class BaseMailIntegrationSimpleTestCase(MailIntegrationAssertionsMixin, LoggedSimpleTestCase):
    """ Define shared MailHog-backed integration helpers for outbound mail. """

    @classmethod
    def setUpClass(cls) -> None:
        """ Skip the suite when MailHog integration is not explicitly enabled. """
        super().setUpClass()

        if not is_mail_integration_enabled():
            raise SkipTest("Mail integration tests are disabled.")

        if settings.EMAIL_BACKEND != "django.core.mail.backends.smtp.EmailBackend":
            raise SkipTest("Mail integration tests require the SMTP email backend.")


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
    EMAIL_HOST="127.0.0.1",
    EMAIL_PORT=1025,
    DEFAULT_FROM_EMAIL="noreply@example.com",
    CELERY_TASK_ALWAYS_EAGER=False,
)
class BaseAsyncMailIntegrationTransactionTestCase(MailIntegrationAssertionsMixin, LoggedTransactionTestCase):
    """ Define shared MailHog-backed integration helpers for asynchronous outbound mail. """

    @classmethod
    def setUpClass(cls) -> None:
        """ Skip the suite when asynchronous MailHog integration is not explicitly enabled. """
        super().setUpClass()

        if not is_async_mail_integration_enabled():
            raise SkipTest("Asynchronous mail integration tests are disabled.")

        if settings.EMAIL_BACKEND != "django.core.mail.backends.smtp.EmailBackend":
            raise SkipTest("Asynchronous mail integration tests require the SMTP email backend.")
