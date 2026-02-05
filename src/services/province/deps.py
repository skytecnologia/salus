from typing import Annotated, TypeAlias

from fastapi import Depends

from src.services.common.deps import EndotoolsClientDep
from src.services.province.service import ProvinceService


def get_province_service(client: EndotoolsClientDep) -> ProvinceService:
    return ProvinceService(client)


ProvinceServiceDep: TypeAlias = Annotated[ProvinceService, Depends(get_province_service)]
