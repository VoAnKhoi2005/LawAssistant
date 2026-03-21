from core.exceptions import NotFoundException
from services.user_service import UserService


class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def get_user_by_id(self, user_id: str):
        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user
