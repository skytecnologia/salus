from fastapi import APIRouter, Request, Response, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.params import Form
from starlette.responses import RedirectResponse

from src.auth.pwd import verify_password, generate_random_password
from src.auth.session import create_session_cookie, SESSION_COOKIE_NAME, SESSION_MAX_AGE, TMP_SESSION_COOKIE_NAME
from src.core.database import DBSessionDep
from src.core.templates import templates

from src.services import user as user_service
from src.services.auth.password_reset import set_password_reset_session, get_password_reset_session
from src.services import email as email_service
from src.services.email import EmailManagerDep
from src.services.user import get_active_user_by_id

router = APIRouter()


@router.get("/login", name="login_page", response_class=HTMLResponse)
def login_page(request: Request, redirect_to: str = None):
    session_error_message = request.session.pop("error_message", None)
    context = {"request": request, "redirect_to": redirect_to}
    if session_error_message:
        context["error_message"] = session_error_message
    return templates.TemplateResponse("auth/login.html", context=context)


@router.post("/login", name="login")
def login(request: Request, db: DBSessionDep, username: str = Form(...), password: str = Form(...),
          redirect_to: str = None):
    user = user_service.get_user_by_username(db, username)
    if not user or not user.is_active or not verify_password(password, user.hashed_password):
        error_message = "Credenciales incorrectas."
        return templates.TemplateResponse("auth/login.html", {"request": request, "error_message": error_message})

    # If password is expired but still usable → mark OTP as used (if it's an OTP)
    if user.is_password_expired:
        if user.otp_password_used:
            # Password is expired and OTP already used → block access
            error_message = "Por seguridad, el acceso de este usuario se encuentra bloqueado"
            return templates.TemplateResponse("auth/login.html", {"request": request, "error_message": error_message})
        else:
            # If password is expired but still usable → mark OTP as used (if it's an OTP)
            user.otp_password_used = True  # burn the OTP or expired password
            db.commit()
            db.refresh(user)
            # Store user ID in session for limited access to the password change page
            set_password_reset_session(request, user.id)
            password_reset_url = request.url_for("password_reset_page")
            return RedirectResponse(password_reset_url, status_code=302)

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


@router.get("/auth/logout", name="logout")
def logout(request: Request, response: Response):
    request.session.clear()
    redirect = RedirectResponse("/login", status_code=302)
    secure_flag = request.url.scheme == "https"
    redirect.delete_cookie(SESSION_COOKIE_NAME, path="/", secure=secure_flag)
    redirect.delete_cookie(TMP_SESSION_COOKIE_NAME, path="/")  # clean reset session, if exists
    return redirect


@router.get("/auth/password-recover", name="password_recover_page", response_class=HTMLResponse)
def password_recover_page(request: Request):
    return templates.TemplateResponse("auth/password-recover.html", {"request": request})


@router.post("/auth/password-recover", name="password_recover", response_class=HTMLResponse)
def password_recover(request: Request, db: DBSessionDep,
                     background_tasks: BackgroundTasks, email_manager: EmailManagerDep, username: str = Form(...)):
    user = user_service.get_user_by_username(db, username)
    if user and user.is_active:
        # Ignore if user does not exists or if is not active. Hide it to avoid give much information to potential malicious users...
        new_password = generate_random_password()
        print(new_password)
        user_service.reset_user_password(db, user, new_password)
        email_list = [user.email]
        email_service.send_password_recover(user, new_password, background_tasks, email_manager, email_list)

    return RedirectResponse(url=request.url_for("recover_confirmation_page"), status_code=303)


@router.get("/auth/recover-confirmation", name="recover_confirmation_page", response_class=HTMLResponse)
def recover_confirmation_page(request: Request):
    return templates.TemplateResponse("auth/recover-confirmation.html", {"request": request})


@router.get("/auth/password-reset", name="password_reset_page", response_class=HTMLResponse)
def password_reset_page(request: Request, db: DBSessionDep):
    session_user_id = get_password_reset_session(request)
    if not session_user_id:
        request.session["error_message"] = "Sesión inválida o caducada."
        return RedirectResponse(url=request.url_for("login_page"), status_code=302)

    user = get_active_user_by_id(db, session_user_id)
    if not user or not user.is_password_expired:
        request.session["error_message"] = "Acceso no autorizado."
        return RedirectResponse(url=request.url_for("login_page"), status_code=302)
    set_password_reset_session(request, user.id)  # Reassign temporary session for POST

    return templates.TemplateResponse("auth/password-reset.html", {"request": request})


@router.post("/auth/password-reset", name="password_reset", response_class=HTMLResponse)
def password_reset(request: Request, db: DBSessionDep, new_password: str = Form(...)):
    session_user_id = get_password_reset_session(request)
    if not session_user_id:
        request.session["error_message"] = "Sesión inválida o caducada."
        return RedirectResponse(url=request.url_for("login_page"), status_code=302)

    user = get_active_user_by_id(db, session_user_id)
    if not user or not user.is_password_expired:
        request.session["error_message"] = "Acceso no autorizado."
        return RedirectResponse(url=request.url_for("login_page"), status_code=302)
    user_service.update_user_password(db, user, new_password)

    # request.session["success_message"] = "Contraseña actualizada correctamente. Inicie sesión."
    return RedirectResponse(url=request.url_for("login_page"), status_code=302)
