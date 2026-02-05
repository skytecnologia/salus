from datetime import datetime
from src.infrastructure.external.endotools.schemas import AppointmentDTO, ExaminationDTO, ReportDTO, InsurerDTO, \
    MunicipalityDTO, ProvinceDTO
from src.schemas.insurer import Insurer
from src.schemas.municipality import Municipality
from src.schemas.patient import Appointment, Examination, Report
from src.schemas.province import Province


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
        report_id=dto.id,
        date=dto.fecha,
        procedure=dto.tipo,
    )


def to_insurer(dto: InsurerDTO) -> Insurer:
    return Insurer(
        name=dto.nombre,
        external_id=dto.id,
    )


def to_municipality(dto: MunicipalityDTO) -> Municipality:
    return Municipality(
        code=dto.codigo,
        name=dto.nombre,
        external_id=dto.id,
    )


def to_province(dto: ProvinceDTO) -> Province:
    return Province(
        code=dto.codigo,
        name=dto.nombre,
        external_id=dto.id,
    )
