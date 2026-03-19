from redis.asyncio import Redis

from core.config import settings
from core.exceptions import UnauthorizedException
from core.security import create_access_token, create_refresh_token, decode_refresh_token
from dto.auth_dto import TokenPairResponse
from dto.user_dto import RegisterRequest, LoginRequest
from services.user_service import UserService


class AuthService:
    def __init__(self, user_service: UserService, redis_client: Redis):
        self.user_service = user_service
        self.redis = redis_client

    async def register(self, request: RegisterRequest) -> dict:
        user = await self.user_service.create_user(request.username, request.email, request.password)
        tokens = await self._issue_tokens(user["id"], user["username"])
        return {"user": user, "tokens": tokens}

    async def login(self, request: LoginRequest) -> dict:
        user_doc = await self.user_service.verify_user_credentials(request.username, request.password)
        user = self.user_service.serialize_user(user_doc)
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

        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")

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
