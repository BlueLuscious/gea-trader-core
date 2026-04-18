""" Public policy exports for the mail package. """

from core.mail.policies.system_mail_sender_policy import SystemMailSenderPolicy
from core.mail.policies.tenant_mail_reply_policy import TenantMailReplyPolicy

__all__: list[str] = [
    "SystemMailSenderPolicy",
    "TenantMailReplyPolicy",
]
