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

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)


    __table_args__ = (
        UniqueConstraint("mrn", "mrn_system"),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="patient", foreign_keys=[user_id])
