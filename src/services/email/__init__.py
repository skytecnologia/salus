from .service import EmailService
from .manager import EmailManager, EmailManagerDep, get_email_manager, EmailData
from .config import EmailType
from .handlers.auth import send_new_user, send_password_reset, send_password_recover

__all__ = [
    "EmailService",
    "EmailManager",
    "EmailManagerDep",
    "EmailData",
    "get_email_manager",
    "EmailType",
    "send_new_user",
    "send_password_reset",
    "send_password_recover"
]
