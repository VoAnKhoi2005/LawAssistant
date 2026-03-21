from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import settings
from core.exceptions import UnauthorizedException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(data: dict, expires_delta: timedelta, secret_key: str) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=settings.algorithm)


def _decode_token(token: str, secret_key: str) -> dict:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError as exc:
        raise UnauthorizedException("Invalid or expired token") from exc


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    delta = expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    return _create_token(data, delta, settings.jwt_secret_key)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    delta = expires_delta or timedelta(days=settings.refresh_token_expire_days)
    return _create_token(data, delta, settings.jwt_refresh_secret_key)


def decode_access_token(token: str) -> dict:
    return _decode_token(token, settings.jwt_secret_key)


def decode_refresh_token(token: str) -> dict:
    return _decode_token(token, settings.jwt_refresh_secret_key)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    if credentials is None:
        raise UnauthorizedException("Authorization header missing")

    payload = decode_access_token(credentials.credentials)
    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    user_controller = getattr(request.app.state, "user_controller", None)
    if user_controller:
        user = await user_controller.user_service.get_user_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")
        return user.model_dump()

    return {"id": user_id, "username": payload.get("username")}
