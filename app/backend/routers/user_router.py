from fastapi import APIRouter, Depends, Request
from controllers.user_controller import UserController
from dto.user_dto import RegisterRequest, LoginRequest
from core.security import get_current_user


def create_user_router(user_controller: UserController) -> APIRouter:
    router = APIRouter(prefix="/api/users", tags=["users"])
    
    @router.post("/register")
    async def register(request: RegisterRequest):
        return await user_controller.register(request)
    
    @router.post("/login")
    async def login(request: LoginRequest):
        return await user_controller.login(request)
    
    @router.get("/me")
    async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
        return await user_controller.get_current_user_profile(current_user["user_id"])
    
    return router


def create_user_router_with_state() -> APIRouter:
    router = APIRouter(prefix="/api/users", tags=["users"])
    
    @router.post("/register")
    async def register(request: RegisterRequest, req: Request):
        return await req.app.state.user_controller.register(request)
    
    @router.post("/login")
    async def login(request: LoginRequest, req: Request):
        return await req.app.state.user_controller.login(request)
    
    @router.get("/me")
    async def get_current_user_profile(req: Request, current_user: dict = Depends(get_current_user)):
        return await req.app.state.user_controller.get_current_user_profile(current_user["user_id"])
    
    return router

