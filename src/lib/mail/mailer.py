from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from pydantic import EmailStr

from src.core.config import email_settings


conf = ConnectionConfig(
    MAIL_USERNAME=email_settings.EMAIL_USERNAME,
    MAIL_PASSWORD=email_settings.EMAIL_PASSWORD,
    MAIL_FROM=email_settings.EMAIL_FROM,
    MAIL_PORT=email_settings.EMAIL_PORT,
    MAIL_SERVER=email_settings.EMAIL_SERVER,
    MAIL_STARTTLS=email_settings.EMAIL_STARTTLS,
    MAIL_SSL_TLS=email_settings.EMAIL_SSL_TLS,
    # USE_CREDENTIALS=email_settings.USE_CREDENTIALS,
    # VALIDATE_CERTS=email_settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=email_settings.EMAIL_TEMPLATE_FOLDER,
)


class FastMailWrapper:
    def __init__(self):
        self.client = FastMail(conf)

    async def send(
        self,
        subject: str,
        recipients: list[EmailStr],
        template_name: str,
        template_data: dict,
        subtype: MessageType = MessageType.html,
    ) -> None:
        bcc: list[str] = []  # Use this to send a copy of the email to another email address, for debugging purposes
        message = MessageSchema(
            subject=subject,
            recipients = recipients,
            template_body=template_data,
            subtype=subtype,
            bcc=bcc
        )
        await self.client.send_message(message, template_name=template_name)


def create_mailer() -> FastMailWrapper:
    return FastMailWrapper()
