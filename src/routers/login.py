from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.params import Form
from starlette.responses import RedirectResponse

from src.auth.pwd import verify_password
from src.auth.session import create_session_cookie, SESSION_COOKIE_NAME, SESSION_MAX_AGE, TMP_SESSION_COOKIE_NAME
from src.core.database import DBSessionDep
from src.core.templates import templates

from src.services import user as user_service

router = APIRouter()


@router.get("/login", name="login_page", response_class=HTMLResponse)
def login_page(request: Request, redirect_to: str = None):
    session_error_message = request.session.pop("error_message", None)
    context = {"request": request, "redirect_to": redirect_to}
    if session_error_message:
        context["error_message"] = session_error_message
    return templates.TemplateResponse("login.html", context=context)


@router.post("/login", name="login")
def login(request: Request, db: DBSessionDep, username: str = Form(...), password: str = Form(...),
          redirect_to: str = None):
    user = user_service.get_user_by_username(db, username)
    if not user or not user.is_active or not verify_password(password, user.hashed_password):
        error_message = "Credenciales incorrectas."
        return templates.TemplateResponse("login.html", {"request": request, "error_message": error_message})

    if user.is_password_expired:
        error_message = "Su contraseña ha expirado. Por favor, cambie su contraseña."
        return templates.TemplateResponse("login.html", {"request": request, "error_message": error_message})

    # Everything OK, proceed to normal login
    request.session.clear()
    session_cookie, csrf_token = create_session_cookie(user.id)

    redirect_url = redirect_to or "/home"
    redirect = RedirectResponse(redirect_url, status_code=302)
    redirect.delete_cookie(TMP_SESSION_COOKIE_NAME, path="/")  # clean reset session, if exists
    # Set the Secure flag automatically when running under HTTPS
    secure_flag = request.url.scheme == "https"
    redirect.set_cookie(
        SESSION_COOKIE_NAME,
        session_cookie,
        httponly=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
        secure=secure_flag,
        path="/",
    )
    return redirect


@router.get("/logout", name="logout")
def logout(request: Request, response: Response):
    request.session.clear()
    redirect = RedirectResponse("/login", status_code=302)
    secure_flag = request.url.scheme == "https"
    redirect.delete_cookie(SESSION_COOKIE_NAME, path="/", secure=secure_flag)
    redirect.delete_cookie(TMP_SESSION_COOKIE_NAME, path="/")  # clean reset session, if exists
    return redirect
