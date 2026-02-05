from datetime import datetime
from src.infrastructure.external.endotools.schemas import DemographicsDTO, CreatePatientRequest
from src.schemas.patient import PatientSummary
from src.schemas.registration import RegistrationForm


def to_patient_summary(dto: DemographicsDTO) -> PatientSummary:
    return PatientSummary(
        mrn=dto.idunico,
        full_name=" ".join(
            part for part in [dto.nombre, dto.apellido1, dto.apellido2] if part
        ),
        birth_date=dto.fechaNacimiento,
        sex=dto.sexo,
        patient_id=dto.id,
    )


def map_registration_to_create_patient(registration_form: RegistrationForm) -> CreatePatientRequest:
    """
    Maps a RegistrationForm to CreatePatientRequest for Endotools API.
    
    Args:
        registration_form: The registration form data with province and municipality names
    
    Returns:
        CreatePatientRequest ready to be sent to Endotools API
    """
    # Map gender: male -> 1, female -> 0
    sexo = 1 if registration_form.gender == "male" else 0
    
    # Format birth date to DD/MM/YYYY
    fecha_nacimiento = registration_form.birth_date.strftime("%d/%m/%Y")
    
    return CreatePatientRequest(
        # idunico=,
        DNI=registration_form.id_document_number,
        nombre=registration_form.given_names,
        apellido1=registration_form.family_name_1,
        apellido2=registration_form.family_name_2,
        sexo=sexo,
        fechaNacimiento=fecha_nacimiento,
        poblacion=registration_form.municipality,
        provincia=registration_form.province,
        telefono1=registration_form.phone_number,
        aseguradora_id=registration_form.insurer_id
    )
