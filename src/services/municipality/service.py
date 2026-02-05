from src.core.config import logger
from src.infrastructure.external.endotools.client import EndotoolsAPIClient
from src.infrastructure.external.endotools.exceptions import ExternalAPIError, ExternalAPINotFoundError
from src.mappers.endotools.data_mapper import to_municipality


class MunicipalityService:
    def __init__(self, client: EndotoolsAPIClient):
        self.client = client

    async def get_municipalities(self):

        try:
            data = await self.client.get_municipalities()
            municipalities = [to_municipality(municipality_dto) for municipality_dto in data]
        except ExternalAPINotFoundError:
            logger.warning(f"Municipalities not found")
            return None
        except ExternalAPIError as e:
            logger.error(f"Failed to get municipalities: {e}")
            return None

        return municipalities
