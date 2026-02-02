from collections.abc import AsyncIterator

from src.infrastructure.external.endotools.client import EndotoolsAPIClient
from src.infrastructure.external.endotools.exceptions import (
    ExternalAPIError, ExternalAPITimeoutError, ExternalAPINotFoundError,
    ExternalAPIAuthenticationError, ExternalAPIPermissionError, ExternalAPIServerError
)
from src.mappers.endotools.patient_mapper import to_patient_summary
from src.mappers.endotools.data_mapper import to_appointment, to_examination, to_report
from src.core.config import logger


class PatientService:
    def __init__(self, client: EndotoolsAPIClient):
        self.client = client

    async def get_full_patient_data(self, mrn: str):
        patient = None
        appointments = []
        examinations = []
        reports = []

        # Get demographics first
        try:
            demo_dto = await self.client.get_demographics(mrn)
            patient = to_patient_summary(demo_dto)
        except ExternalAPINotFoundError:
            logger.warning(f"Patient not found with MRN: {mrn}")
            return None
        except ExternalAPIError as e:
            logger.error(f"Failed to get demographics for MRN {mrn}: {e}")
            # Continue with empty data if demographics fail

        # Get appointments (only if we have patient data)
        if patient:
            try:
                appointments_dto = await self.client.get_appointments(mrn)
                appointments = [to_appointment(apt) for apt in appointments_dto]
            except ExternalAPIError as e:
                logger.error(f"Failed to get appointments for MRN {mrn}: {e}")

        # Get examinations (only if we have patient data)
        if patient:
            try:
                exams_dto = await self.client.get_examinations(patient.patient_id)
                examinations = [to_examination(exam) for exam in exams_dto]
            except ExternalAPIError as e:
                logger.error(f"Failed to get examinations for patient ID {patient.mrn}: {e}")

        # Get reports for each examination
        for exam in examinations:
            try:
                reports_dto = await self.client.get_reports(exam.exam_id)
                reports.extend([to_report(report) for report in reports_dto])
            except ExternalAPIError as e:
                logger.warning(f"Failed to get reports for exam {exam.exam_id}: {e}")
                # Continue with other exams even if one fails

        return {
            "patient": patient,
            "appointments": appointments,
            "examinations": examinations,
            "reports": reports,
        }

    async def get_patient_data(self, mrn: str):
        patient = {}

        try:
            data = await self.client.get_demographics(mrn)
            patient = to_patient_summary(data)
        except ExternalAPINotFoundError:
            logger.warning(f"Patient not found with MRN: {mrn}")
            return None
        except ExternalAPIError as e:
            logger.error(f"Failed to get demographics for MRN {mrn}: {e}")
            # Continue with empty data if demographics fail

        return patient

    async def get_appointments_data(self, mrn: str):
        appointments = []
        try:
            appointments_dto = await self.client.get_appointments(mrn)
            appointments = [to_appointment(apt) for apt in appointments_dto]
        except ExternalAPIError as e:
            logger.error(f"Failed to get appointments for MRN {mrn}: {e}")
        return appointments

    async def get_examinations_data(self, mrn: str):
        patient = None
        examinations = []

        # Get demographics first
        try:
            demo_dto = await self.client.get_demographics(mrn)
            patient = to_patient_summary(demo_dto)
        except ExternalAPINotFoundError:
            logger.warning(f"Patient not found with MRN: {mrn}")
            return None
        except ExternalAPIError as e:
            logger.error(f"Failed to get demographics for MRN {mrn}: {e}")
            # Continue with empty data if demographics fail

        # Get examinations (only if we have patient data)
        if patient:
            try:
                exams_dto = await self.client.get_examinations(patient.patient_id)
                examinations = [to_examination(exam) for exam in exams_dto]
            except ExternalAPIError as e:
                logger.error(f"Failed to get examinations for patient ID {patient.mrn}: {e}")

            # Get reports for each examination
            for exam in examinations:
                try:
                    reports_dto = await self.client.get_reports(exam.exam_id)
                    if len(reports_dto) > 0:
                        # add flag indicating report available
                        exam.is_report_available = True
                except ExternalAPIError as e:
                    logger.warning(f"Failed to get reports for exam {exam.exam_id}: {e}")
                    # Continue with other exams even if one fails

        return examinations

    async def get_exam_last_report(self, exploration_id: int, ) -> AsyncIterator[bytes]:
        """
        get_last_report is an async generator
        StreamingResponse consumes it lazily
        The httpx connection stays open while chunks are yielded
        When streaming finishes or client disconnects → context managers exit cleanly
        """
        return self.client.get_last_report(exploration_id)
