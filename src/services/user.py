from sqlalchemy.orm import Session, selectinload

from sqlalchemy import select
from src.models import User


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
