import os
import logging
import logging.config

from functools import lru_cache
from pathlib import Path
from yaml import safe_load

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, EmailStr


def _root_dir():
    """Returns the root directory of the project, as a string."""
    return str(Path(__file__).parent.parent.parent)


def _validate_path(sub_path: str):
    """
    Returns (as string) the path of a given sub-path, taking the project root directory as base root.
    Create a sub-path if not exists.
    """
    path = str(Path(_root_dir()) / sub_path)
    if not Path(path).exists():
        print(f'Creating path {path}...')
        Path(path).mkdir(parents=True)
    return path


class GlobalSettings(BaseSettings):
    """
    Set application global settings.
    Generally, should not be used directly. Use the global_settings() function, decorated with @lru_cache, below.
    Here, the variables are uppercase because they are treated as global variables, during the running of the app.
    """
    APP_NAME: str = 'salus'
    # database settings
    DATABASE_DIALECT: str
    DATABASE_HOST: str
    DATABASE_PORT: str | None = None
    DATABASE_NAME: str
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    # configuration path and files
    PATH_CONFIG: str = str(_root_dir() / Path('conf'))
    LOGGER_CONFIG: str = str(PATH_CONFIG / Path('logger.yaml'))
    # app base paths / directories
    ROOT_DIR: str = _root_dir()
    PATH_LOGS: str = str(Path(ROOT_DIR) / 'logs')
    # middleware and session
    SECRET_KEY: str
    # Endotools API settings
    ENDOTOOLS_BASE_URL: str
    ENDOTOOLS_KEY: str
    ENDOTOOLS_TIMEOUT: int | None = 30

    @field_validator('ENDOTOOLS_TIMEOUT', mode='before')
    @classmethod
    def parse_timeout(cls, v):
        if v == '' or v is None:
            return None
        return int(v)


@lru_cache()
def global_settings() -> GlobalSettings:
    _settings = GlobalSettings()

    # Ensure required directories exist at startup
    for path in [
        _settings.PATH_LOGS,
    ]:
        os.makedirs(path, exist_ok=True)

    return _settings


# Import this into modules to access global settings
settings = global_settings()
"""Global Settings"""


class EmailSettings(BaseSettings):
    EMAIL_SERVER: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: EmailStr
    EMAIL_FROM_NAME: str = "App Notifications"
    EMAIL_STARTTLS: bool
    EMAIL_SSL_TLS: bool
    EMAIL_TEMPLATE_FOLDER: str

    model_config = SettingsConfigDict(env_ignore_empty=True)


@lru_cache()
def email_settings() -> EmailSettings:
    return EmailSettings()


# Import this into modules to access email settings
email_settings = email_settings()
"""Global Email Settings"""


def configure_logging():
    """ Logger configuration """
    config_file = settings.LOGGER_CONFIG
    with open(config_file) as f:
        config = safe_load(f)

    # Dynamically update the log file path
    log_path = Path(settings.PATH_LOGS) / f"{settings.APP_NAME}.log"
    config["handlers"]["main_file"]["filename"] = str(log_path)

    logging.config.dictConfig(config)


# import this if you want to log to app main logger
# In global settings, APP_NAME should be defined in the logger configuration file.
logger = logging.getLogger(settings.APP_NAME)
""" App main logger """
