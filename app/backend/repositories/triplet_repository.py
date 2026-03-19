from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId


class TripletRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["triplets"]
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find().skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_by_id(self, triplet_id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": ObjectId(triplet_id)})
    
    async def find_by_subject(self, subject_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find({"subject_id.$oid": subject_id}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_by_object(self, object_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find({"object_id.$oid": object_id}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def create(self, triplet_data: dict) -> dict:
        result = await self.collection.insert_one(triplet_data)
        triplet_data["_id"] = str(result.inserted_id)
        return triplet_data
    
    async def update(self, triplet_id: str, triplet_data: dict) -> Optional[dict]:
        await self.collection.update_one(
            {"_id": ObjectId(triplet_id)},
            {"$set": triplet_data}
        )
        return await self.find_by_id(triplet_id)
    
    async def delete(self, triplet_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(triplet_id)})
        return result.deleted_count > 0
