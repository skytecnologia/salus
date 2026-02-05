from typing import Annotated, TypeAlias

from fastapi import Depends

from src.services.common.deps import EndotoolsClientDep
from src.services.insurer.service import InsurerService


def get_insurer_service(client: EndotoolsClientDep) -> InsurerService:
    return InsurerService(client)


InsurerServiceDep: TypeAlias = Annotated[InsurerService, Depends(get_insurer_service)]
