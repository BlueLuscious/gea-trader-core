""" Project-wide Celery tasks for outbound mail delivery. """

import logging
from smtplib import SMTPException
from celery import shared_task
from core.mail.serializers import MailMessagePayloadSerializer, TemplateMailRequestPayloadSerializer
from core.mail.services import MailService, TemplateMailService

logger = logging.getLogger(__name__)

MAIL_TASK_AUTORETRY_EXCEPTIONS: tuple[type[BaseException], ...] = (
    SMTPException,
    TimeoutError,
    ConnectionError,
)
MAIL_TASK_MAX_RETRIES = 3
MAIL_TASK_RETRY_BACKOFF_MAX_SECONDS = 300


@shared_task(
    name="core.tasks.mail.send_mail_message_task",
    autoretry_for=MAIL_TASK_AUTORETRY_EXCEPTIONS,
    max_retries=MAIL_TASK_MAX_RETRIES,
    retry_backoff=True,
    retry_backoff_max=MAIL_TASK_RETRY_BACKOFF_MAX_SECONDS,
    retry_jitter=True,
)
def send_mail_message_task(payload: dict, fail_silently: bool = False) -> int:
    """ Rebuild one raw mail payload and send it through the project mail service.

    Args:
        payload: Serialized outbound mail payload.
        fail_silently: Whether transport errors should be swallowed.

    Returns:
        int: Number of successfully delivered messages.
    """
    logger.info(
        "Executing raw mail task subject=%r recipients=%s fail_silently=%s",
        payload.get("subject"),
        len(payload.get("to", [])),
        fail_silently,
    )
    message = MailMessagePayloadSerializer.deserialize(payload)
    return MailService.send(message, fail_silently=fail_silently)


@shared_task(
    name="core.tasks.mail.send_templated_mail_task",
    autoretry_for=MAIL_TASK_AUTORETRY_EXCEPTIONS,
    max_retries=MAIL_TASK_MAX_RETRIES,
    retry_backoff=True,
    retry_backoff_max=MAIL_TASK_RETRY_BACKOFF_MAX_SECONDS,
    retry_jitter=True,
)
def send_templated_mail_task(payload: dict, fail_silently: bool = False) -> int:
    """ Rebuild one templated mail payload and send it through the templated mail service.

    Args:
        payload: Serialized templated mail payload.
        fail_silently: Whether transport errors should be swallowed.

    Returns:
        int: Number of successfully delivered messages.
    """
    logger.info(
        "Executing templated mail task subject=%r recipients=%s fail_silently=%s",
        payload.get("subject"),
        len(payload.get("to", [])),
        fail_silently,
    )
    request = TemplateMailRequestPayloadSerializer.deserialize(payload)
    return TemplateMailService.send(request, fail_silently=fail_silently)
