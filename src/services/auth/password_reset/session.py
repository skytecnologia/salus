"""
Session utilities for the password reset flow.

This module handles session-based state used to validate temporary access
to the password reset page. It uses FastAPI's built-in SessionMiddleware.

Usage:
- Set the session when redirecting after login if password is expired.
- Validate and optionally reassign the session for GET/POST password reset.
- Clear session values to prevent reuse after completion or error.

Note:
This is separate from the login session, which is managed via a stateless cookie
in `service.auth.session`.
"""
from typing import Optional

_PASSWORD_RESET_SESSION_USER_KEY = "password_reset_user_id"
_PASSWORD_RESET_SESSION_TS_KEY = "password_reset_ts"
_PASSWORD_RESET_SESSION_EXPIRATION_MINUTES = 10

from datetime import datetime, timezone, timedelta

from fastapi import Request

def set_password_reset_session(request: Request, user_id: int) -> None:
    request.session[_PASSWORD_RESET_SESSION_USER_KEY] = user_id
    request.session[_PASSWORD_RESET_SESSION_TS_KEY] = datetime.now(timezone.utc).isoformat()


def get_password_reset_session(request: Request) -> Optional[int]:
    user_id = request.session.pop(_PASSWORD_RESET_SESSION_USER_KEY, None)
    ts_str = request.session.pop(_PASSWORD_RESET_SESSION_TS_KEY, None)

    if not user_id or not ts_str or not isinstance(ts_str, str):
        return None

    try:
        ts = datetime.fromisoformat(ts_str)
    except ValueError:
        return None

    now = datetime.now(timezone.utc)
    if now - ts > timedelta(minutes=_PASSWORD_RESET_SESSION_EXPIRATION_MINUTES):
        return None

    return user_id


def clear_password_reset_session(request: Request) -> None:
    """Remove password reset session data from the request session."""
    request.session.pop(_PASSWORD_RESET_SESSION_USER_KEY, None)
    request.session.pop(_PASSWORD_RESET_SESSION_TS_KEY, None)
