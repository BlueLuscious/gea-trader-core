""" Project-level outbound templated mail service. """

import logging
from celery.result import AsyncResult
from core.mail.composers import TemplateMailComposer
from core.mail.dtos import TemplateMailRequestDTO
from core.mail.serializers import TemplateMailRequestPayloadSerializer
from core.mail.services.mail_service import MailService


logger = logging.getLogger(__name__)


class TemplateMailService:
    """ Send outbound mail rendered from Django templates. """

    composer_class = TemplateMailComposer
    mail_service_class = MailService
    payload_serializer_class = TemplateMailRequestPayloadSerializer

    @classmethod
    def send(cls, request: TemplateMailRequestDTO, fail_silently: bool = False) -> int:
        """ Render one template pair and send the resulting outbound message.

        Args:
            request: Templated outbound mail request.
            fail_silently: Whether transport errors should be swallowed.

        Returns:
            int: Number of successfully delivered messages.
        """
        message = cls.composer_class.compose(request)
        delivered_count = cls.mail_service_class.send(message, fail_silently=fail_silently)
        logger.info(
            "Delivered templated mail subject=%r recipients=%s explicit_tenant=%s delivered_count=%s fail_silently=%s",
            request.subject,
            len(request.to),
            request.tenant is not None,
            delivered_count,
            fail_silently,
        )
        return delivered_count

    @classmethod
    def send_async(cls, request: TemplateMailRequestDTO, fail_silently: bool = False) -> AsyncResult:
        """ Enqueue one templated mail request for asynchronous delivery.

        Args:
            request: Templated outbound mail request.
            fail_silently: Whether transport errors should be swallowed in the worker.

        Returns:
            AsyncResult: Celery async result handle for the queued task.
        """
        from core.tasks.mail.tasks import send_templated_mail_task

        payload = cls.payload_serializer_class.serialize(request)
        async_result = send_templated_mail_task.delay(payload=payload, fail_silently=fail_silently)
        logger.info(
            "Enqueued templated mail task_id=%s subject=%r recipients=%s explicit_tenant=%s fail_silently=%s",
            async_result.id,
            request.subject,
            len(request.to),
            request.tenant is not None,
            fail_silently,
        )
        return async_result
