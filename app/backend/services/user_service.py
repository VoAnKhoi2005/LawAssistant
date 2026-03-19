from typing import Optional
from fastapi import HTTPException, status
from core.security import hash_password, verify_password, create_access_token
from repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def register_user(self, username: str, email: str, password: str) -> dict:
        existing_user = await self.user_repository.find_by_username(username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        existing_email = await self.user_repository.find_by_email(email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        hashed_password = hash_password(password)
        user_data = {
            "username": username,
            "email": email,
            "password": hashed_password
        }
        
        created_user = await self.user_repository.create(user_data)
        return {
            "id": created_user["_id"],
            "username": created_user["username"],
            "email": created_user["email"]
        }
    
    async def authenticate_user(self, username: str, password: str) -> dict:
        user = await self.user_repository.find_by_username(username)
        if not user or not verify_password(password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        access_token = create_access_token(
            data={"sub": str(user["_id"]), "username": user["username"]}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"]
            }
        }
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            return None
        
        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"]
        }
