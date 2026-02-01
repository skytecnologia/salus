from datetime import datetime
from src.infrastructure.external.endotools.schemas import DemographicsDTO
from src.schemas.patient import PatientSummary


def to_patient_summary(dto: DemographicsDTO) -> PatientSummary:
    return PatientSummary(
        mrn=dto.idunico,
        full_name=" ".join(
            part for part in [dto.nombre, dto.apellido1, dto.apellido2] if part
        ),
        birth_date=dto.fechaNacimiento,
        sex=dto.sexo,
        patient_id=dto.id,
    )
