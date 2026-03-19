from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from bson import ObjectId


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
    
    async def create(self, user_data: dict) -> dict:
        result = await self.collection.insert_one(user_data)
        user_data["_id"] = str(result.inserted_id)
        return user_data
