from fastapi import APIRouter, Depends, Request

from controllers.user_controller import UserController
from core.security import get_current_user
from utils.api_response_helper import success_response


def create_user_router(user_controller: UserController) -> APIRouter:
    router = APIRouter(prefix="/api/users", tags=["users"])

    @router.get("/me")
    async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
        data = await user_controller.get_user_by_id(current_user["id"])
        return success_response(data, message="User profile retrieved")

    return router


def create_user_router_with_state() -> APIRouter:
    router = APIRouter(prefix="/api/users", tags=["users"])

    @router.get("/me")
    async def get_current_user_profile(
        req: Request, current_user: dict = Depends(get_current_user)
    ):
        data = await req.app.state.user_controller.get_user_by_id(current_user["id"])
        return success_response(data, message="User profile retrieved")

    return router
