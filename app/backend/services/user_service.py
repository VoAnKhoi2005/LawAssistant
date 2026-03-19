from typing import Optional

from core.exceptions import ConflictException, NotFoundException, UnauthorizedException
from core.security import hash_password, verify_password
from repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(self, username: str, email: str, password: str) -> dict:
        username_exists = await self.user_repository.find_by_username(username)
        if username_exists:
            raise ConflictException("Username already exists")

        email_exists = await self.user_repository.find_by_email(email)
        if email_exists:
            raise ConflictException("Email already exists")

        hashed_password = hash_password(password)
        user_data = {
            "username": username,
            "email": email,
            "password": hashed_password,
        }
        created_user = await self.user_repository.create(user_data)
        return self._sanitize_user(created_user)

    async def verify_user_credentials(self, username: str, password: str) -> dict:
        user = await self.user_repository.find_by_username(username)
        if not user or not verify_password(password, user["password"]):
            raise UnauthorizedException("Incorrect username or password")
        return user

    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            return None
        return self._sanitize_user(user)

    async def get_user_by_username(self, username: str) -> dict:
        user = await self.user_repository.find_by_username(username)
        if not user:
            raise NotFoundException("User not found")
        return self._sanitize_user(user)

    def serialize_user(self, user_doc: dict) -> dict:
        return self._sanitize_user(user_doc)

    @staticmethod
    def _sanitize_user(user_doc: dict) -> dict:
        return {
            "id": str(user_doc["_id"]),
            "username": user_doc["username"],
            "email": user_doc["email"],
        }
