from typing import Annotated, TypeAlias

from fastapi import Depends

from src.core.config import settings
from src.infrastructure.external.endotools.client import EndotoolsAPIClient


def get_endotools_client() -> EndotoolsAPIClient:
    """Create and configure Endotools API client."""
    return EndotoolsAPIClient(
        base_url=settings.ENDOTOOLS_BASE_URL,
        auth_key=settings.ENDOTOOLS_KEY,
        timeout=settings.ENDOTOOLS_TIMEOUT
    )


EndotoolsClientDep: TypeAlias = Annotated[EndotoolsAPIClient, Depends(get_endotools_client)]
