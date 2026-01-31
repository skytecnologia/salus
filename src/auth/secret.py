import os
from itsdangerous import URLSafeSerializer
from src.core.config import settings

# Load serializer secret from the environment for security; fall back with a warning for development
_secret = os.getenv("SESSION_SECRET") or os.getenv("SECRET_KEY")
if not _secret:
    # In production, ensure SESSION_SECRET is set
    print("[WARN] SESSION_SECRET not set. Using default key from .env. Set SESSION_SECRET in environment!")
    _secret = settings.SECRET_KEY
serializer = URLSafeSerializer(_secret)
