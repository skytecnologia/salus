from typing import Annotated, TypeAlias

from fastapi import Request, Depends, HTTPException, status, Form
from itsdangerous import BadSignature

from src.auth.secret import serializer
from src.auth.session import SESSION_COOKIE_NAME, SESSION_MAX_AGE, SESSION_USER_KEY, get_csrf_token
from src.core.database import DBSessionDep

from src.models import User
from src.services import user as user_service


# Retrieve current user from cookie
def get_current_user(request: Request, db: DBSessionDep) -> User | None:
    """
    Return user from session cookie, if valid and active.
    If cookie is invalid, return None.
    Below an annotated dependency is defined, for convenience.
    """
    session_cookie = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_cookie:
        return None
    try:
        data = serializer.loads(session_cookie, max_age=SESSION_MAX_AGE)
        user_id = data.get(SESSION_USER_KEY)
        return user_service.get_active_user_by_id(db, user_id)
    except BadSignature:
        return None


CurrentUserDep: TypeAlias = Annotated[User | None, Depends(get_current_user)]


def get_login_required_user(user: CurrentUserDep) -> User:
    """
    Check if the user is logged in, raising an exception if not.
    Depends on the function that returns the user from the session cookie, if valid.
    Below an annotated dependency is defined, for convenience.
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    return user


LoginRequiredDep: TypeAlias = Annotated[User, Depends(get_login_required_user)]


def csrf_protect(request: Request, csrf_token: str = Form(..., alias="_csrf")) -> None:
    """
    Dependency to protect state-changing routes via CSRF token validation.
    Expects a form field named `_csrf` to be submitted with the request.
    """
    session_token = get_csrf_token(request)
    if not session_token or csrf_token != session_token:
        raise HTTPException(status_code=403, detail="Invalid CSRF token!")


# Create a reusable, typed dependency alias
CsrfProtectDep: TypeAlias = Annotated[None, Depends(csrf_protect)]
