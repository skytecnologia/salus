from sqlalchemy.orm import Session

from src.core.config import logger
from src.infrastructure.external.endotools.client import EndotoolsAPIClient
from src.infrastructure.external.endotools.exceptions import ExternalAPIError, ExternalAPINotFoundError
from src.mappers.endotools.patient_mapper import map_registration_to_create_patient
from src.schemas.registration import RegistrationForm
from src.services import user as user_service
from src.services.common.exceptions import UserAlreadyExistsError, UserPatientDataError


class RegistrationService:
    def __init__(self, db: Session, client: EndotoolsAPIClient):
        self.db = db
        self.client = client

    async def create_patient(self, registration_form: RegistrationForm) -> str:
        """
        Create a new patient in Endotools using registration form data.
        
        Args:
            registration_form: The registration form data
            
        Returns:
            The created patient ID if successful
            
        Raises:
            UserAlreadyExistsError: If the user or patient already exists in the system
            ExternalAPIError: If there's an error creating the patient in Endotools
        """

        id_document_number = registration_form.id_document_number

        # Check if user already exists in local database
        existing_user = user_service.get_user_by_username(self.db, str(id_document_number))
        if existing_user:
            logger.warning(f"Attempted to register existing user: {id_document_number}")
            raise UserAlreadyExistsError("El usuario ya existe.")

        # Check if patient already exists in Endotools
        try:
            existing_patient = await self.client.get_patient_by_document(id_document_number)
            # If we get here, patient exists (no exception was raised)
            logger.warning(f"Attempted to register existing patient with ID: {id_document_number}")
            raise UserAlreadyExistsError("El paciente ya existe en el sistema externo.")
        except ExternalAPINotFoundError:
            # Patient not found - this is expected, we can proceed with creation
            logger.info(f"Patient not found in Endotools, proceeding with creation: {id_document_number}")
        except ExternalAPIError as e:
            # Any other API error should prevent patient creation
            logger.error(f"Error checking patient existence in Endotools: {e}")
            raise ExternalAPIError(f"Error al verificar si el paciente existe: {e}")
        
        # Map registration form to Endotools create patient request
        create_patient_request = map_registration_to_create_patient(registration_form)
        # Call Endotools API to create patient
        response = await self.client.create_patient(create_patient_request)
        # Get new patient demographics
        demographics = await self.client.get_patient_by_document(id_document_number)
        # Double check patient data
        if demographics.id != int(response.id):
            logger.warning(f"Patient ID mismatch: {demographics.id} != {response.id}")
            raise UserPatientDataError("El paciente no se pudo crear correctamente.")
        
        # Build full name from demographics
        full_name = " ".join(
            part for part in [demographics.nombre, demographics.apellido1, demographics.apellido2] if part
        )
        
        # Generate password from birth date (DDMMYYYY format)
        if demographics.fechaNacimiento:
            password = demographics.fechaNacimiento.strftime("%d%m%Y")
        else:
            # Fallback if no birth date
            password = id_document_number
        
        # Create User and Patient in local database
        try:
            user, patient = user_service.create_user_with_patient(
                db=self.db,
                username=id_document_number,
                name=full_name,
                email=str(registration_form.email),
                phone=None,
                password=password,
                mrn=demographics.idunico,
                mrn_system="endotools",
                date_of_birth=demographics.fechaNacimiento
            )
            logger.info(f"User and Patient created in database: user_id={user.id}, patient_id={patient.id}")
        except Exception as e:
            logger.error(f"Failed to create User and Patient in database: {e}")
            raise
        
        logger.info(f"Patient registration completed successfully with ID: {response.id}")
        return response.id
