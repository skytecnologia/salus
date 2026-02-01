from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

from src.auth.deps import LoginRequiredDep
from src.core.templates import templates
from src.services.patient.deps import PatientServiceDep

router = APIRouter()


@router.get("/", name="redirect_home", response_class=HTMLResponse)
async def redirect_home():
    return RedirectResponse(url="/home", status_code=302)

@router.get("/home", name="home_page", response_class=HTMLResponse)
async def home_page(request: Request, user: LoginRequiredDep, patient_service: PatientServiceDep):

    patient = user.patient
    patient_data = {}
    
    if patient:
        patient_data = await patient_service.get_full_patient_data(patient.mrn)
        if patient_data is None:
            # Patient not found in external system
            patient_data = {}

    print("DATA", patient_data)
    context = {"request": request, "user": user, "patient": patient_data}
    return templates.TemplateResponse("home.html", context=context)

