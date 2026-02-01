from typing import TypeAlias, Annotated

from fastapi import Depends

from src.core.config import settings
from src.infrastructure.external.endotools.client import EndotoolsAPIClient
from src.services.patient.service import PatientService


def get_ehr_client() -> EndotoolsAPIClient:
    return EndotoolsAPIClient(base_url=settings.ENDOTOOLS_BASE_URL,
                              auth_key=settings.ENDOTOOLS_KEY,
                              timeout=settings.ENDOTOOLS_TIMEOUT)


def get_patient_service(client: EndotoolsAPIClient = Depends(get_ehr_client)) -> PatientService:
    return PatientService(client)


PatientServiceDep: TypeAlias = Annotated[PatientService, Depends(get_patient_service)]
