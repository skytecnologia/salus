from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class EmailConfig:
    subject: str
    template: str


class EmailType(str, Enum):
    WELCOME = "welcome"
    ADMIN_PASSWORD_RESET = "admin_password_reset"
    USER_PASSWORD_RECOVER = "user_password_recover"


EMAIL_CONFIGS = {
    EmailType.WELCOME: EmailConfig(
        subject="Bienvenido a ZENO",
        template="welcome.html"
    ),
    EmailType.ADMIN_PASSWORD_RESET: EmailConfig(
        subject="Notificación de Cambio de Contraseña",
        template="password-reset.html"
    ),
    EmailType.USER_PASSWORD_RECOVER: EmailConfig(
        subject="Notificación de Recuperación de Contraseña",
        template="password-recover.html"
    )
}


def get_email_config(email_type: EmailType) -> EmailConfig:
    try:
        return EMAIL_CONFIGS[email_type]
    except KeyError:
        raise ValueError(f"No email configuration found for type {email_type}")
