

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get("/", name="home_page", response_class=HTMLResponse)
async def home_page(request: Request):
    return "Home"
