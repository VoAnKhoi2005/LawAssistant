from redis.asyncio import Redis

from core.config import settings
from core.exceptions import ConflictException, NotFoundException, UnauthorizedException
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from dto.auth_dto import TokenPairResponse
from dto.user_dto import RegisterRequest, LoginRequest
from repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository, redis_client: Redis):
        self.user_repository = user_repository
        self.redis = redis_client

    async def register(self, request: RegisterRequest) -> dict:
        existing_username = await self.user_repository.find_by_username(request.username)
        if existing_username:
            raise ConflictException("Username already exists")

        existing_email = await self.user_repository.find_by_email(request.email)
        if existing_email:
            raise ConflictException("Email already exists")

        user_doc = await self.user_repository.create(
            {
                "username": request.username,
                "email": request.email,
                "password": hash_password(request.password),
            }
        )

        user = self._sanitize_user(user_doc)
        tokens = await self._issue_tokens(user["id"], user["username"])
        return {"user": user, "tokens": tokens}

    async def login(self, request: LoginRequest) -> dict:
        user_doc = await self.user_repository.find_by_username(request.username)
        if not user_doc or not verify_password(request.password, user_doc["password"]):
            raise UnauthorizedException("Incorrect username or password")

        user = self._sanitize_user(user_doc)
        tokens = await self._issue_tokens(user["id"], user["username"])
        return {"user": user, "tokens": tokens}

    async def refresh_tokens(self, refresh_token: str) -> dict:
        payload = decode_refresh_token(refresh_token)
        user_id = payload.get("sub")
        username = payload.get("username")
        if not user_id or not username:
            raise UnauthorizedException("Invalid refresh token payload")

        stored_token = await self.redis.get(self._refresh_token_key(user_id))
        if not stored_token or stored_token != refresh_token:
            raise UnauthorizedException("Refresh token is invalid or has expired")

        user_doc = await self.user_repository.find_by_id(user_id)
        if not user_doc:
            raise NotFoundException("User not found")

        user = self._sanitize_user(user_doc)
        tokens = await self._issue_tokens(user_id, username)
        return {"user": user, "tokens": tokens}

    async def logout(self, user_id: str) -> None:
        await self.redis.delete(self._refresh_token_key(user_id))

    async def _issue_tokens(self, user_id: str, username: str) -> TokenPairResponse:
        access_token = create_access_token({"sub": user_id, "username": username})
        refresh_token = create_refresh_token({"sub": user_id, "username": username})
        await self.redis.set(
            self._refresh_token_key(user_id),
            refresh_token,
            ex=settings.refresh_token_expire_days * 24 * 60 * 60,
        )
        return TokenPairResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
            refresh_expires_in=settings.refresh_token_expire_days * 24 * 60 * 60,
        )

    @staticmethod
    def _refresh_token_key(user_id: str) -> str:
        return f"refresh_token:{user_id}"

    @staticmethod
    def _sanitize_user(user_doc: dict) -> dict:
        return {
            "id": str(user_doc["_id"]),
            "username": user_doc["username"],
            "email": user_doc["email"],
        }
