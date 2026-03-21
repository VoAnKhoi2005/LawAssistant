from typing import Optional

from core.exceptions import NotFoundException
from repositories.user_repository import UserRepository
from models.user_model import User


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        user_dict = await self.user_repository.find_by_id(user_id)
        if not user_dict:
            return None
        return self._dict_to_user(user_dict)

    async def get_user_by_username(self, username: str) -> User:
        user_dict = await self.user_repository.find_by_username(username)
        if not user_dict:
            raise NotFoundException("User not found")
        return self._dict_to_user(user_dict)

    def serialize_user(self, user_doc: dict) -> User:
        return self._dict_to_user(user_doc)

    @staticmethod
    def _dict_to_user(user_dict: dict) -> User:
        return User(
            _id=str(user_dict["_id"]),
            username=user_dict["username"],
            email=user_dict["email"],
            password=user_dict["password"]
        )
