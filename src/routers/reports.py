from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse

from src.auth.deps import LoginRequiredDep
from src.core.templates import templates
from src.services.patient.deps import PatientServiceDep

router = APIRouter()


@router.get("/informes", name="reports_page", response_class=HTMLResponse)
async def reports_page(request: Request, user: LoginRequiredDep, patient_service: PatientServiceDep):
    patient = user.patient
    examinations_data = []
    if patient:
        examinations_data = await patient_service.get_examinations_data(patient.mrn)

    print(examinations_data)
    context = {"request": request, "user": user, "patient": patient, "examinations": examinations_data}
    return templates.TemplateResponse("reports.html", context=context)


@router.get("/examinations/{examination_id}/report")
async def download_report(examination_id: int, _user: LoginRequiredDep, patient_service: PatientServiceDep):

    stream = await patient_service.get_exam_last_report(examination_id)

    # it will leave the frontend decide if downalod or open in new tab.
    # if want to force download, use "Content-Disposition": "attachment; filename=report.pdf" instead
    return StreamingResponse(
        stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline; filename=informe.pdf"
        },
    )
