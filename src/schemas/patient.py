from pydantic import BaseModel
from datetime import date, time


# schemas related to the patient domain

class PatientSummary(BaseModel):
    mrn: str
    full_name: str
    birth_date: date | None
    sex: str | None
    patient_id: int


class Appointment(BaseModel):
    appointment_id: int
    date: date
    time: time
    procedure: str | None


class Examination(BaseModel):
    exam_id: int
    date: date
    service: str | None
    procedure: str | None
    physician: str | None
    is_report_available: bool | None = False


class Report(BaseModel):
    report_id: str
    date: date
    procedure: str | None
