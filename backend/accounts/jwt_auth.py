"""
JWT utilities for app_token generation and verification.
"""
import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.http import HttpRequest

from .models import User


def _get_jwt_secret() -> str:
    secret = getattr(settings, 'DJANGO_JWT_SECRET', None)
    if not secret:
        raise ValueError("DJANGO_JWT_SECRET is not configured in settings.")
    return secret


def generate_app_token(user: User) -> str:
    payload = {
        'user_id': user.id,
        'email': user.email,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(seconds=getattr(settings, 'JWT_EXPIRES_SECONDS', 2592000)),
    }
    return jwt.encode(payload, _get_jwt_secret(), algorithm='HS256')


def verify_app_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, _get_jwt_secret(), algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def extract_user_from_request(request: HttpRequest) -> User | None:
    token = request.COOKIES.get('app_token')
    if not token:
        return None
    payload = verify_app_token(token)
    if not payload:
        return None
    try:
        return User.objects.get(id=payload['user_id'])
    except User.DoesNotExist:
        return None
