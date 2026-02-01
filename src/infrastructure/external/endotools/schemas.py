from pydantic import BaseModel


class DemographicsDTO(BaseModel):
    patient_id: str
    nombre: str
    apellido: str
    fecha_nacimiento: str
    sexo: str | None

    class Config:
        extra = "ignore"  # Explicitly ignore extra fields


class AppointmentDTO(BaseModel):
    cita_id: str
    fecha: str
    tipo: str

    class Config:
        extra = "ignore"


class ExaminationDTO(BaseModel):
    exploracion_id: str
    fecha: str
    descripcion: str

    class Config:
        extra = "ignore"


class ReportDTO(BaseModel):
    informe_id: str
    titulo: str
    contenido: str

    class Config:
        extra = "ignore"
