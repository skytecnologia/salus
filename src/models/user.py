from typing import Optional, List

from sqlalchemy import Integer, Identity, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.common.mixins import AuditMixin, SoftDeleteMixin


class User(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_password_expired: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    otp_password_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="user", foreign_keys="Patient.user_id")
