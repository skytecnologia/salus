from src.core.config import logger
from src.infrastructure.external.endotools.client import EndotoolsAPIClient
from src.infrastructure.external.endotools.exceptions import ExternalAPIError, ExternalAPINotFoundError
from src.mappers.endotools.data_mapper import to_province


class ProvinceService:
    def __init__(self, client: EndotoolsAPIClient):
        self.client = client

    async def get_provinces(self):

        try:
            data = await self.client.get_provinces()
            provinces = [to_province(province_dto) for province_dto in data]
        except ExternalAPINotFoundError:
            logger.warning(f"Provinces not found")
            return None
        except ExternalAPIError as e:
            logger.error(f"Failed to get provinces: {e}")
            return None

        return provinces
