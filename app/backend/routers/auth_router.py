from fastapi import APIRouter, Depends, Request

from controllers.auth_controller import AuthController
from core.security import get_current_user
from dto.auth_dto import RefreshTokenRequest
from dto.user_dto import LoginRequest, RegisterRequest
from utils.response import success_response


def create_auth_router_with_state() -> APIRouter:
    router = APIRouter(prefix="/api/auth", tags=["auth"])

    @router.post("/register")
    async def register(request_body: RegisterRequest, req: Request):
        result = await req.app.state.auth_controller.register(request_body)
        return success_response(result, message="User registered successfully")

    @router.post("/login")
    async def login(request_body: LoginRequest, req: Request):
        result = await req.app.state.auth_controller.login(request_body)
        return success_response(result, message="User logged in successfully")

    @router.post("/refresh")
    async def refresh_token(request_body: RefreshTokenRequest, req: Request):
        result = await req.app.state.auth_controller.refresh(request_body)
        return success_response(result, message="Token refreshed successfully")

    @router.post("/logout")
    async def logout(req: Request, current_user: dict = Depends(get_current_user)):
        result = await req.app.state.auth_controller.logout(current_user["id"])
        return success_response(result, message="User logged out successfully")

    return router
