from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId


class DocumentRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["documents"]
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find().skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_by_id(self, document_id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": ObjectId(document_id)})
    
    async def find_by_so_hieu(self, so_hieu: str) -> Optional[dict]:
        return await self.collection.find_one({"so_hieu": so_hieu})
    
    async def create(self, document_data: dict) -> dict:
        result = await self.collection.insert_one(document_data)
        document_data["_id"] = str(result.inserted_id)
        return document_data
    
    async def update(self, document_id: str, document_data: dict) -> Optional[dict]:
        await self.collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": document_data}
        )
        return await self.find_by_id(document_id)
    
    async def delete(self, document_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0
