from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

from src.auth.deps import LoginRequiredDep
from src.core.templates import templates

router = APIRouter()


@router.get("/", name="redirect_home", response_class=HTMLResponse)
async def redirect_home():
    return RedirectResponse(url="/home", status_code=302)

@router.get("/home", name="home_page", response_class=HTMLResponse)
async def home_page(request: Request, user: LoginRequiredDep):
    context = {"request": request, "user": user}
    return templates.TemplateResponse("home.html", context=context)

