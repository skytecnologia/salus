from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from src.auth.deps import LoginRequiredDep
from src.core.templates import templates
from src.services.patient.deps import PatientServiceDep

router = APIRouter()


@router.get("/citas", name="appointments_page", response_class=HTMLResponse)
async def appointments_page(request: Request, user: LoginRequiredDep, patient_service: PatientServiceDep):
    patient = user.patient
    appointments_data = []
    if patient:
        appointments_data = await patient_service.get_appointments_data(patient.mrn)

    context = {"request": request, "user": user, "patient": patient, "appointments": appointments_data}
    return templates.TemplateResponse("appointments.html", context=context)
