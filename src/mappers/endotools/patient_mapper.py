from datetime import datetime
from src.infrastructure.external.endotools.schemas import DemographicsDTO
from src.schemas.patient import PatientSummary


def to_patient_summary(dto: DemographicsDTO) -> PatientSummary:
    return PatientSummary(
        mrn=dto.patient_id,
        full_name=f"{dto.nombre} {dto.apellido}",
        birth_date=datetime.strptime(dto.fecha_nacimiento, "%Y-%m-%d").date(),
        sex=dto.sexo,
    )
