""" Project-wide outbound mail task exports. """

from core.tasks.mail.tasks import send_mail_message_task, send_templated_mail_task

__all__: list[str] = [
    "send_mail_message_task",
    "send_templated_mail_task",
]
