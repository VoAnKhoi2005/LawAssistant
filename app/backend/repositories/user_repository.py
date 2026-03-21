from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from bson import ObjectId

from models.user_model import User


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["users"]
    
    async def find_by_username(self, username: str) -> Optional[dict]:
        return await self.collection.find_one({"username": username})
    
    async def find_by_email(self, email: str) -> Optional[dict]:
        return await self.collection.find_one({"email": email})
    
    async def find_by_id(self, user_id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": ObjectId(user_id)})
    
    async def create(self, user: User) -> User:
        user_dict = user.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        return User(**user_dict)
