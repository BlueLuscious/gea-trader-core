""" Project-wide asynchronous task packages. """

from core.tasks.mail import send_mail_message_task, send_templated_mail_task

__all__: list[str] = [
    "send_mail_message_task",
    "send_templated_mail_task",
]
