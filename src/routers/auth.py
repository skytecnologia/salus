from fastapi import APIRouter, Request, Response, BackgroundTasks, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.params import Form
from starlette.responses import RedirectResponse
from datetime import date

from src.auth.pwd import verify_password, generate_random_password
from src.auth.session import create_session_cookie, SESSION_COOKIE_NAME, SESSION_MAX_AGE, TMP_SESSION_COOKIE_NAME
from src.core.config import logger
from src.core.database import DBSessionDep
from src.core.templates import templates
from src.schemas.registration import RegistrationForm, registration_form_dependency

from src.services import user as user_service
from src.services.auth.password_reset import set_password_reset_session, get_password_reset_session
from src.services import email as email_service
from src.services.email import EmailManagerDep
from src.services.insurer.deps import InsurerServiceDep
from src.services.municipality.deps import MunicipalityServiceDep
from src.services.province.deps import ProvinceServiceDep
from src.services.user import get_active_user_by_id
from src.services.auth.register.deps import RegistrationServiceDep
from src.services.common.exceptions import UserAlreadyExistsError, UserPatientDataError
from src.infrastructure.external.endotools.exceptions import ExternalAPIError

router = APIRouter()


@router.get("/login", name="login_page", response_class=HTMLResponse)
def login_page(request: Request, redirect_to: str = None):
    session_error_message = request.session.pop("error_message", None)
    session_success_message = request.session.pop("success_message", None)
    context = {"request": request, "redirect_to": redirect_to}
    if session_error_message:
        context["error_message"] = session_error_message
    if session_success_message:
        context["success_message"] = session_success_message
    return templates.TemplateResponse("auth/login.html", context=context)


@router.post("/login", name="login")
def login(request: Request, db: DBSessionDep, username: str = Form(...), password: str = Form(...),
          redirect_to: str = None):
    user = user_service.get_user_by_username(db, username)
    if not user or not user.is_active or not verify_password(password, user.hashed_password):
        request.session["error_message"] = "Credenciales incorrectas."
        return RedirectResponse(url=request.url_for("login_page"), status_code=302)

    # If password is expired but still usable → mark OTP as used (if it's an OTP)
    if user.is_password_expired:
        if user.otp_password_used:
            # Password is expired and OTP already used → block access
            request.session["error_message"] = "Por seguridad, el acceso de este usuario se encuentra bloqueado"
            return RedirectResponse(url=request.url_for("login_page"), status_code=302)
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
    redirect = RedirectResponse(request.url_for("login_page"), status_code=302)
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


@router.get("/auth/register", name="registration_form", response_class=HTMLResponse)
async def registration_form(
        request: Request,
        insurer_service: InsurerServiceDep,
        municipality_service: MunicipalityServiceDep,
        province_service: ProvinceServiceDep,
):
    insurers = await insurer_service.get_insurers() or []
    municipalities = await municipality_service.get_municipalities() or []
    provinces = await province_service.get_provinces() or []
    # if not insurers or not municipalities or not provinces:
    #     request.session["error_message"] = "No se encontraron datos para registrar un usuario."
    #     return "KAO"

    session_error_message = request.session.pop("error_message", None)
    context = {"request": request, "insurers": insurers, "municipalities": municipalities, "provinces": provinces}
    if session_error_message:
        context["error_message"] = session_error_message
    return templates.TemplateResponse("auth/register.html", context=context)


@router.post("/auth/register", name="registration_submit", response_class=HTMLResponse)
async def registration_submit(
        request: Request,
        db: DBSessionDep,
        registration_service: RegistrationServiceDep,
        form_data: RegistrationForm = Depends(registration_form_dependency),
):
    try:
        # Create patient in Endotools
        patient_id = await registration_service.create_patient(form_data)
        
        # Store success message in session
        request.session["success_message"] = f"Registro completado exitosamente. ID del paciente: {patient_id}"
        
    except UserAlreadyExistsError as e:
        # User already exists → redirect to login
        logger.warning(f"Registration failed - user already exists: {form_data.email}")
        request.session["error_message"] = str(e)
        return RedirectResponse(url=request.url_for("login_page"), status_code=302)

    except UserPatientDataError as e:
        # Patient data validation error → back to form to correct
        logger.error(f"Registration failed - patient data error: {e}")
        request.session["error_message"] = str(e)
        return RedirectResponse(url=request.url_for("registration_form"), status_code=302)

    except ExternalAPIError as e:
        # Error communicating with Endotools API → back to form to retry
        logger.error(f"Registration failed - API error: {e}")
        request.session["error_message"] = "Error al crear el paciente. Por favor, inténtelo de nuevo."
        return RedirectResponse(url=request.url_for("registration_form"), status_code=302)

    except Exception as e:
        # Unexpected error → back to form to retry
        logger.error(f"Registration failed - unexpected error: {e}")
        request.session["error_message"] = "Ha ocurrido un error inesperado. Por favor, inténtelo de nuevo."
        return RedirectResponse(url=request.url_for("registration_form"), status_code=302)

    # Success → redirect to login page
    return RedirectResponse(url=request.url_for("login_page"), status_code=302)
