from src.core.config import logger
from src.infrastructure.external.endotools.client import EndotoolsAPIClient
from src.infrastructure.external.endotools.exceptions import ExternalAPINotFoundError, ExternalAPIError
from src.mappers.endotools.data_mapper import to_insurer


class InsurerService:
    def __init__(self, client: EndotoolsAPIClient):
        self.client = client

    async def get_insurers(self):

        try:
            data = await self.client.get_insurers()
            insurers = [to_insurer(insurer_dto) for insurer_dto in data]
        except ExternalAPINotFoundError:
            logger.warning(f"Insurers not found")
            return None
        except ExternalAPIError as e:
            logger.error(f"Failed to get insurers: {e}")
            return None
        
        return insurers
