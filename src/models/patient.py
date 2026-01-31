from datetime import date
from typing import List

from sqlalchemy import Integer, Identity, String, Date, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.common.mixins import AuditMixin, SoftDeleteMixin


class Patient(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)

    mrn: Mapped[str] = mapped_column(String(64), nullable=False)
    mrn_system: Mapped[str | None] = mapped_column(String(128), nullable=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[date | None]

    __table_args__ = (
        UniqueConstraint("mrn", "mrn_system"),
    )

    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary="user_patients",
        back_populates="patients",
    )


class UserPatient(Base):
    __tablename__ = "user_patients"

    user_id = mapped_column(ForeignKey("users.id"), primary_key=True)
    patient_id = mapped_column(ForeignKey("patients.id"), primary_key=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_patients")
    patient: Mapped["Patient"] = relationship("Patient", back_populates="user_patients")
