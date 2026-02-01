from pydantic import BaseModel
from datetime import date


# schemas related to the patient domain

class PatientSummary(BaseModel):
    mrn: str
    full_name: str
    birth_date: date
    sex: str | None


class Appointment(BaseModel):
    appointment_id: str
    date: date
    type: str


class Examination(BaseModel):
    exam_id: str
    date: date
    description: str


class Report(BaseModel):
    report_id: str
    title: str
    url: str
