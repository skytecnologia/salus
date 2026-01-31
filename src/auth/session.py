import secrets

from fastapi import Request
from itsdangerous import BadSignature

from src.auth.secret import serializer

SESSION_COOKIE_NAME = "session"
TMP_SESSION_COOKIE_NAME = "_session"  # Temporary session cookie name, used on reset password flow
SESSION_MAX_AGE = 7200  # 2 hours
SESSION_USER_KEY = "user_id"
SESSION_CSRF_KEY = "csrf"


def create_session_cookie(user_id: int):
    csrf_token = secrets.token_urlsafe(32)
    session_data = {SESSION_USER_KEY: user_id, SESSION_CSRF_KEY: csrf_token}
    return serializer.dumps(session_data), csrf_token


def get_csrf_token(request: Request):
    session_cookie = request.cookies.get(SESSION_COOKIE_NAME)
    if session_cookie:
        try:
            data = serializer.loads(session_cookie, max_age=SESSION_MAX_AGE)
            return data.get(SESSION_CSRF_KEY)
        except BadSignature:
            return None
    return None
