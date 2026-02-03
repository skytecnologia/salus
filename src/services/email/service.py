from typing import Any

from fastapi_mail import MessageType
from src.lib.mail import FastMailWrapper

from .config import EmailConfig


class EmailService:
    def __init__(self, mailer: FastMailWrapper):
        self.mailer = mailer

    async def send_email(self, config: EmailConfig, recipients: list[str], context: dict[str, Any]) -> None:
        try:
            await self.mailer.send(
                subject=config.subject,
                recipients=recipients,
                template_name=config.template,
                template_data=context,
                subtype=MessageType.html
            )
        except Exception as e:
            # Log the error here!
            print(f"Failed to send email '{config.subject}': {e}")
