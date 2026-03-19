from fastapi import HTTPException, status
from services.user_service import UserService
from dto.user_dto import RegisterRequest, LoginRequest, UserResponse, LoginResponse


class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    async def register(self, request: RegisterRequest):
        return await self.user_service.register_user(
            request.username,
            request.email,
            request.password
        )
    
    async def login(self, request: LoginRequest):
        return await self.user_service.authenticate_user(
            request.username,
            request.password
        )
    
    async def get_current_user_profile(self, user_id: str):
        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
