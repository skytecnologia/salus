from typing import Annotated, TypeAlias

from fastapi import Depends

from src.core.database import DBSessionDep
from src.services.common.deps import EndotoolsClientDep
from src.services.auth.register.service import RegistrationService


def get_registration_service(db: DBSessionDep, client: EndotoolsClientDep) -> RegistrationService:
    return RegistrationService(db, client)


RegistrationServiceDep: TypeAlias = Annotated[RegistrationService, Depends(get_registration_service)]
