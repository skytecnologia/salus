from sqlalchemy.orm import Session, selectinload
from datetime import date

from sqlalchemy import select

from src.auth.pwd import hash_password
from src.models import User
from src.models.patient import Patient
from src.core.config import logger


def get_user_by_username(db: Session, username: str):
    stmt = select(User).where(User.username == username)
    return db.execute(stmt).scalar_one_or_none()


def get_active_user_by_id(db: Session, user_id: int | None) -> type[User] | None:
    if user_id is None:
        return None
    stmt = (
        select(User)
        .where(User.id == user_id, User.is_active == True)
    )
    return db.execute(stmt).scalar_one_or_none()


def update_user_password(db: Session, user: User, password: str) -> User:
    hashed_password = hash_password(password)
    user.hashed_password = hashed_password
    # Update password logic; reset flags to normal use, after user update his password.
    user.is_password_expired = False
    user.otp_password_used = False
    db.commit()
    db.refresh(user)

    return user


def reset_user_password(db: Session, user: User, password: str) -> User:
    hashed_password = hash_password(password)
    user.hashed_password = hashed_password
    # Update password logic; set an OTP and set it expired, to force user to change upon login.
    user.is_password_expired = True
    user.otp_password_used = False
    db.commit()
    db.refresh(user)

    return user


def create_user_with_patient(
    db: Session,
    username: str,
    name: str,
    email: str,
    phone: str | None,
    password: str,
    mrn: str,
    mrn_system: str,
    date_of_birth: date | None
) -> tuple[User, Patient]:
    """
    Create a User and associated Patient in a single transaction.
    
    Args:
        db: Database session
        username: Username (typically ID document number)
        name: Full name of the user/patient
        email: Email address
        phone: Phone number (optional)
        password: Plain text password to be hashed
        mrn: Medical Record Number
        mrn_system: MRN system identifier (e.g., "endotools")
        date_of_birth: Patient's date of birth
        
    Returns:
        Tuple of (User, Patient) objects
        
    Raises:
        Exception: If either User or Patient creation fails, rolls back the entire transaction
    """
    try:
        # Create User
        user = User(
            username=username,
            name=name,
            email=email,
            phone=phone,
            hashed_password=hash_password(password),
            is_password_expired=True,
            otp_password_used=False,
            is_active=True,
            is_superuser=False
        )
        db.add(user)
        db.flush()  # Flush to get the user.id without committing
        
        # Create Patient linked to User
        patient = Patient(
            mrn=mrn,
            mrn_system=mrn_system,
            name=name,
            date_of_birth=date_of_birth,
            user_id=user.id
        )
        db.add(patient)
        
        # Commit both records
        db.commit()
        db.refresh(user)
        db.refresh(patient)
        
        logger.info(f"User and Patient created successfully: username={username}, user_id={user.id}, patient_id={patient.id}")
        return user, patient
        
    except Exception as e:
        # Rollback on any error
        db.rollback()
        logger.error(f"Failed to create User and Patient for username={username}: {e}")
        raise

