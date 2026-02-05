from typing import TypeAlias, Annotated

from fastapi import Depends

from src.services.common.deps import EndotoolsClientDep
from src.services.patient.service import PatientService


def get_patient_service(client: EndotoolsClientDep) -> PatientService:
    return PatientService(client)


PatientServiceDep: TypeAlias = Annotated[PatientService, Depends(get_patient_service)]
