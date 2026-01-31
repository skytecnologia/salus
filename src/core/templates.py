from fastapi.templating import Jinja2Templates

from src.core.config import settings

directory = "/".join((settings.ROOT_DIR, "src/templates"))
templates = Jinja2Templates(directory=directory)
