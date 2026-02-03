from dataclasses import dataclass
from typing import Any, Annotated, TypeAlias, List

from fastapi import Request, Depends

from .config import EmailType, get_email_config
from .service import EmailService


@dataclass
class EmailData:
    type: EmailType
    context: dict
    recipients: List[str]


class EmailManager:
    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    async def send_email(
        self,
        email_type: EmailType,
        recipients: list[str],
        context: dict[str, Any]
    ) -> None:
        config = get_email_config(email_type)
        await self.email_service.send_email(
            config=config,
            recipients=recipients,
            context=context
        )


def get_email_manager(request: Request) -> EmailManager:
    """ Return singleton EmailManager from the app's shared state """
    return request.app.state.email_manager

# Dependency
#EmailManagerDep: TypeAlias = Annotated[EmailService, Depends(get_email_manager)]
EmailManagerDep: TypeAlias = Annotated[EmailManager, Depends(get_email_manager)]
