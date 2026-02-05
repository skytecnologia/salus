from pydantic import BaseModel, Field, EmailStr
from datetime import date
from fastapi.params import Form


class RegistrationForm(BaseModel):
    given_names: str = Field(..., min_length=1, max_length=100)
    family_name_1: str = Field(..., min_length=1, max_length=100)
    family_name_2: str = Field("", max_length=100)
    gender: str = Field(..., pattern="^(male|female)$")
    id_document_number: str = Field(..., min_length=1, max_length=20)
    phone_number: str = Field(..., min_length=1, max_length=20)
    email: EmailStr = Field(...)
    birth_date: date = Field(...)
    insurer_id: int = Field(...)
    province: str = Field(...)
    municipality: str = Field(...)


async def registration_form_dependency(
    given_names: str = Form(...),
    family_name_1: str = Form(...),
    family_name_2: str = Form(""),
    gender: str = Form(...),
    id_document_number: str = Form(...),
    phone_number: str = Form(...),
    email: str = Form(...),
    birth_date: date = Form(...),
    insurer_id: int = Form(...),
    province: str = Form(...),
    municipality: str = Form(...),
) -> RegistrationForm:
    return RegistrationForm(
        given_names=given_names,
        family_name_1=family_name_1,
        family_name_2=family_name_2,
        gender=gender,
        id_document_number=id_document_number,
        phone_number=phone_number,
        email=email,
        birth_date=birth_date,
        insurer_id=insurer_id,
        province=province,
        municipality=municipality
    )
