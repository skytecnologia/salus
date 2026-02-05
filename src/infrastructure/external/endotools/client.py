import httpx
from collections.abc import AsyncIterator

from .schemas import DemographicsDTO, AppointmentDTO, ExaminationDTO, ReportDTO, ProvinceDTO, MunicipalityDTO, \
    InsurerDTO
from .exceptions import (
    ExternalAPIError, ExternalAPITimeoutError, ExternalAPINotFoundError,
    ExternalAPIAuthenticationError, ExternalAPIPermissionError, ExternalAPIServerError
)
from src.core.config import logger


class EndotoolsAPIClient:
    def __init__(self, base_url: str, auth_key: str, timeout: int = 30):
        self._base_url = base_url
        self._headers = {"cookie": f"i18next=es; authkit={auth_key}"}
        self._timeout = timeout

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            headers=self._headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()

    def _handle_response_error(self, response: httpx.Response):
        """Handle HTTP response errors and raise appropriate exceptions"""
        if response.status_code == 401:
            logger.error(f"Authentication failed for {response.url}")
            raise ExternalAPIAuthenticationError("Authentication failed")
        elif response.status_code == 403:
            logger.error(f"Permission denied for {response.url}")
            raise ExternalAPIPermissionError("Permission denied")
        elif response.status_code == 404:
            logger.warning(f"Resource not found: {response.url}")
            raise ExternalAPINotFoundError("Resource not found")
        elif 500 <= response.status_code < 600:
            logger.error(f"Server error: {response.status_code} for {response.url}")
            raise ExternalAPIServerError(f"Server error: {response.status_code}")
        else:
            logger.error(f"API error: {response.status_code} for {response.url}")
            raise ExternalAPIError(f"API error: {response.status_code}")

    async def get_demographics(self, mrn: str) -> DemographicsDTO:
        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout,
                                         headers=self._headers) as client:
                resp = await client.get("/rest/pacientes.json", params={"idunico": mrn, "deshabilitado": 0})
                if not resp.is_success:
                    self._handle_response_error(resp)

                data = resp.json()
                # Normalize API
                if isinstance(data, list):
                    if not data:
                        raise ExternalAPINotFoundError(f"No demographics found for MRN: {mrn}")
                    data = data[0]
                if not isinstance(data, dict):
                    raise ExternalAPIError(f"Unexpected response format for MRN {mrn}:  {type(data).__name__}")

                return DemographicsDTO.model_validate(data)
        except httpx.TimeoutException:
            logger.error(f"Timeout getting demographics for MRN: {mrn}")
            raise ExternalAPITimeoutError("Request timed out")
        except httpx.RequestError as e:
            logger.error(f"Request error getting demographics for MRN {mrn}: {e}")
            raise ExternalAPIError(f"Request failed: {e}")

    async def get_appointments(self, mrn: str) -> list[AppointmentDTO]:
        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout,
                                         headers=self._headers) as client:
                resp = await client.get("/rest/citas.json", params={"id_unico_paciente": mrn})
                print("RESP", resp)
                if not resp.is_success:
                    self._handle_response_error(resp)
                return [AppointmentDTO.model_validate(a) for a in resp.json()]
        except httpx.TimeoutException:
            logger.error(f"Timeout getting appointments for MRN: {mrn}")
            raise ExternalAPITimeoutError("Request timed out")
        except httpx.RequestError as e:
            logger.error(f"Request error getting appointments for MRN {mrn}: {e}")
            raise ExternalAPIError(f"Request failed: {e}")

    async def get_examinations(self, patient_id: int) -> list[ExaminationDTO]:
        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout,
                                         headers=self._headers) as client:
                resp = await client.get("/rest/exploraciones.json",
                                        params={"estado": 1, "paciente_id": str(patient_id)})
                if not resp.is_success:
                    self._handle_response_error(resp)
                return [ExaminationDTO.model_validate(e) for e in resp.json()]
        except httpx.TimeoutException:
            logger.error(f"Timeout getting examinations for patient ID: {patient_id}")
            raise ExternalAPITimeoutError("Request timed out")
        except httpx.RequestError as e:
            logger.error(f"Request error getting examinations for patient ID {patient_id}: {e}")
            raise ExternalAPIError(f"Request failed: {e}")

    async def get_reports(self, exploracion_id: int) -> list[ReportDTO]:
        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout,
                                         headers=self._headers) as client:
                resp = await client.get("/rest/informes.json", params={"exploracion_id": str(exploracion_id)})
                if not resp.is_success:
                    self._handle_response_error(resp)
                return [ReportDTO.model_validate(r) for r in resp.json()]
        except httpx.TimeoutException:
            logger.error(f"Timeout getting reports for exploration ID: {exploracion_id}")
            raise ExternalAPITimeoutError("Request timed out")
        except httpx.RequestError as e:
            logger.error(f"Request error getting reports for exploration ID {exploracion_id}: {e}")
            raise ExternalAPIError(f"Request failed: {e}")

    async def get_last_report(self, exploration_id: int) -> AsyncIterator[bytes]:
        """ Stream examination last report """
        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout,
                                         headers=self._headers) as client:
                async with client.stream("GET", f"/rest/exploraciones/{exploration_id}/informes/_LAST.pdf", ) as resp:
                    if not resp.is_success:
                        self._handle_response_error(resp)
                    async for chunk in resp.aiter_bytes():
                        yield chunk
        except httpx.TimeoutException:
            logger.error(f"Timeout getting last report for exploration ID: {exploration_id}")
            raise ExternalAPITimeoutError("Request timed out")
        except httpx.RequestError as e:
            logger.error(f"Request error getting last report for exploration ID {exploration_id}: {e}")
            raise ExternalAPIError(f"Request failed: {e}")

    async def get_provinces(self) -> list[ProvinceDTO]:
        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout,
                                         headers=self._headers) as client:
                resp = await client.get("/rest/poblaciones.json",)
                if not resp.is_success:
                    self._handle_response_error(resp)
                return [ProvinceDTO.model_validate(r) for r in resp.json()]
        except httpx.TimeoutException:
            logger.error(f"Timeout getting provinces from endotools")
            raise ExternalAPITimeoutError("Request timed out")
        except httpx.RequestError as e:
            logger.error(f"Request error getting provinces")
            raise ExternalAPIError(f"Request failed: {e}")

    async def get_municipalities(self) -> list[MunicipalityDTO]:
        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout,
                                         headers=self._headers) as client:
                resp = await client.get("/rest/provincias.json",)
                if not resp.is_success:
                    self._handle_response_error(resp)
                return [MunicipalityDTO.model_validate(r) for r in resp.json()]
        except httpx.TimeoutException:
            logger.error(f"Timeout getting municipalities from endotools")
            raise ExternalAPITimeoutError("Request timed out")
        except httpx.RequestError as e:
            logger.error(f"Request error getting municipalities")
            raise ExternalAPIError(f"Request failed: {e}")

    async def get_insurers(self) -> list[InsurerDTO]:
        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout,
                                         headers=self._headers) as client:
                resp = await client.get("/rest/aseguradoras.json",)
                if not resp.is_success:
                    self._handle_response_error(resp)
                return [InsurerDTO.model_validate(r) for r in resp.json()]
        except httpx.TimeoutException:
            logger.error(f"Timeout getting insurers from endotools")
            raise ExternalAPITimeoutError("Request timed out")
        except httpx.RequestError as e:
            logger.error(f"Request error getting insurers")
            raise ExternalAPIError(f"Request failed: {e}")
        