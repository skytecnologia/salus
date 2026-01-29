from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.core.config import configure_logging, logger

from src.routers.home import router as home_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # logging configuration
    configure_logging()

    try:
        yield
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(home_router)
