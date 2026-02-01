from datetime import date, time, datetime
from pydantic import BaseModel, model_validator, ConfigDict

from src.core.config import logger


class DemographicsDTO(BaseModel):
    model_config = ConfigDict(
        extra="ignore"
    )

    id: int
    idunico: str
    nombre: str
    apellido1: str | None = None
    apellido2: str | None = None
    fechaNacimiento: date | None = None
    sexo: str | None = None

    # Pre-processing validator for the whole model, before Pydantic parsing
    @model_validator(mode="before")
    def preprocess_fields(cls, values: dict) -> dict:
        dob = values.get("fechaNacimiento")

        if dob in (None, ""):
            values["fechaNacimiento"] = None
            return values

        if isinstance(dob, date):
            values["fechaNacimiento"] = dob
            return values

        # Try known formats
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                values["fechaNacimiento"] = datetime.strptime(dob, fmt).date()
                return values
            except ValueError:
                continue

        logger.warning("Invalid fechaNacimiento received: %r", dob)
        values["fechaNacimiento"] = None
        return values


class AppointmentDTO(BaseModel):
    model_config = ConfigDict(
        extra="ignore"
    )

    id: int
    fecha: date | None = None
    hora: time | None = None
    exploracion_id: int | None = None
    tipo_exploracion: str | None = None

    @model_validator(mode="before")
    def preprocess_fields(cls, values: dict) -> dict:
        # --- Extract tipo_exploracion.nombre ---
        tipo = values.get("tipoExploracion")
        if isinstance(tipo, dict):
            values["tipo_exploracion"] = tipo.get("nombre")
        else:
            values["tipo_exploracion"] = None

        # --- Parse fecha ---
        f = values.get("fecha")
        if f in (None, ""):
            values["fecha"] = None
        elif isinstance(f, date):
            values["fecha"] = f
        else:
            # try common formats
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    values["fecha"] = datetime.strptime(f, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                logger.warning("Invalid fecha received: %r", f)
                values["fecha"] = None

        # --- Parse hora ---
        h = values.get("hora")
        if h in (None, ""):
            values["hora"] = None
        elif isinstance(h, time):
            values["hora"] = h
        else:
            # try parsing HH:MM or HH:MM:SS
            for fmt in ("%H:%M:%S", "%H:%M"):
                try:
                    values["hora"] = datetime.strptime(h, fmt).time()
                    break
                except ValueError:
                    continue
            else:
                logger.warning("Invalid hora received: %r", h)
                values["hora"] = None

        return values


class ExaminationDTO(BaseModel):
    model_config = ConfigDict(
        extra="ignore"
    )

    id: int
    fecha: date | None = None
    servicio: str | None = None
    tipo: str | None = None
    medico: str | None = None

    @model_validator(mode="before")
    def preprocess_fields(cls, values: dict) -> dict:
        # --- Parse fecha ---
        f = values.get("fecha")
        if f in (None, ""):
            values["fecha"] = None
        elif isinstance(f, date):
            values["fecha"] = f
        else:
            # try common formats
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    values["fecha"] = datetime.strptime(f, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                logger.warning("Invalid fecha received: %r", f)
                values["fecha"] = None

        # --- Extract servicio.nombre ---
        tipo = values.get("servicio")
        if isinstance(tipo, dict):
            values["servicio"] = tipo.get("nombre")
        else:
            values["servicio"] = None

        # --- Extract tipo_exploracion.nombre ---
        tipo = values.get("tipoExploracion")
        if isinstance(tipo, dict):
            values["tipo"] = tipo.get("nombre")
        else:
            values["tipo"] = None

        # --- Extract medico.nombre ---
        tipo = values.get("medico")
        if isinstance(tipo, dict):
            values["medico"] = tipo.get("nombre")
        else:
            values["medico"] = None

        return values


class ReportDTO(BaseModel):
    model_config = ConfigDict(
        extra="ignore"
    )

    informe_id: str
    titulo: str
    contenido: str
