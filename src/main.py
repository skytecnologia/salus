from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from src.core.config import settings, configure_logging
from src.lib.mail import create_mailer

from src.routers.auth import router as login_router
from src.routers.home import router as home_router
from src.routers.appointments import router as appointment_router
from src.routers.reports import router as report_router
from src.services.email import EmailService, EmailManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # logging configuration
    configure_logging()

    # Create the mailer and email-related services / components
    mailer = create_mailer()
    email_service = EmailService(mailer)
    email_manager = EmailManager(email_service)
    # Store them in app.state for global access (ignore ide warning as starlette will inject state to app)
    app.state.mailer = mailer  # type: ignore
    app.state.email_service = email_service  # type: ignore
    app.state.email_manager = email_manager  # type: ignore

    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    # session_cookie=TMP_SESSION_COOKIE_NAME,
    # max_age=1800,  # Optional: session expiry in seconds (e.g. 30 mins)
    # same_site="lax",  # Optional: adjust for CSRF protection
    # https_only=True,  # Optional: True if using HTTPS
)

app.include_router(login_router)
app.include_router(home_router)
app.include_router(appointment_router)
app.include_router(report_router)
