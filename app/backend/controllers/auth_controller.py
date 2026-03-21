from dto.user_dto import RegisterRequest, LoginRequest
from dto.auth_dto import RefreshTokenRequest
from services.auth_service import AuthService


class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    async def register(self, request: RegisterRequest):
        return await self.auth_service.register(request)

    async def login(self, request: LoginRequest):
        return await self.auth_service.login(request)

    async def refresh(self, request: RefreshTokenRequest):
        return await self.auth_service.refresh_tokens(request.refresh_token)

    async def logout(self, user_id: str):
        await self.auth_service.logout(user_id)
        return {"message": "Successfully logged out"}
