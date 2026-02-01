from datetime import datetime
from src.infrastructure.external.endotools.schemas import AppointmentDTO, ExaminationDTO, ReportDTO
from src.schemas.patient import Appointment, Examination, Report


def to_appointment(dto: AppointmentDTO) -> Appointment:
    return Appointment(
        appointment_id=dto.id,
        date=dto.fecha,
        time=dto.hora,
        procedure=dto.tipo_exploracion,
    )


def to_examination(dto: ExaminationDTO) -> Examination:
    return Examination(
        exam_id=dto.id,
        date=dto.fecha,
        service=dto.servicio,
        procedure=dto.tipo,
        physician=dto.medico
    )


def to_report(dto: ReportDTO) -> Report:
    return Report(
        report_id=dto.informe_id,
        title=dto.titulo,
        url=f"/reports/{dto.informe_id}",  # Generate URL for report access
    )
