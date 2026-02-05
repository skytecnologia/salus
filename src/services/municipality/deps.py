from typing import Annotated, TypeAlias

from fastapi import Depends

from src.services.common.deps import EndotoolsClientDep
from src.services.municipality.service import MunicipalityService


def get_municipality_service(client: EndotoolsClientDep) -> MunicipalityService:
    return MunicipalityService(client)


MunicipalityServiceDep: TypeAlias = Annotated[MunicipalityService, Depends(get_municipality_service)]
