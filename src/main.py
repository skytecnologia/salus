from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from src.core.config import settings, configure_logging

from src.routers.login import router as login_router
from src.routers.home import router as home_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # logging configuration
    configure_logging()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    #session_cookie=TMP_SESSION_COOKIE_NAME,
    #max_age=1800,  # Optional: session expiry in seconds (e.g. 30 mins)
    # same_site="lax",  # Optional: adjust for CSRF protection
    # https_only=True,  # Optional: True if using HTTPS
)

app.include_router(login_router)
app.include_router(home_router)
