from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId


class RelationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["relations"]
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find().skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_by_id(self, relation_id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": ObjectId(relation_id)})
    
    async def find_by_relation_name(self, relation_name: str, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find({"relation_name": relation_name}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def create(self, relation_data: dict) -> dict:
        result = await self.collection.insert_one(relation_data)
        relation_data["_id"] = str(result.inserted_id)
        return relation_data
    
    async def update(self, relation_id: str, relation_data: dict) -> Optional[dict]:
        await self.collection.update_one(
            {"_id": ObjectId(relation_id)},
            {"$set": relation_data}
        )
        return await self.find_by_id(relation_id)
    
    async def delete(self, relation_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(relation_id)})
        return result.deleted_count > 0
