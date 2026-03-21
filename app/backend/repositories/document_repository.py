from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId

from models.document_model import Document


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
    
    async def find_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """Find all documents belonging to a specific user"""
        cursor = self.collection.find({"user_id": user_id}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def create(self, document: Document) -> Document:
        document_dict = document.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(document_dict)
        document_dict["_id"] = result.inserted_id
        return Document(**document_dict)
    
    async def create_from_dict(self, document_data: dict) -> dict:
        """Legacy method for dict-based creation"""
        result = await self.collection.insert_one(document_data)
        document_data["_id"] = result.inserted_id
        return document_data
    
    async def update(self, document_id: str, document: Document) -> Optional[Document]:
        document_dict = document.model_dump(by_alias=True, exclude={"id"})
        await self.collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": document_dict}
        )
        updated_dict = await self.find_by_id(document_id)
        if updated_dict:
            updated_dict["_id"] = str(updated_dict["_id"])
            return Document(**updated_dict)
        return None
    
    async def update_from_dict(self, document_id: str, document_data: dict) -> Optional[dict]:
        """Legacy method for dict-based updates"""
        await self.collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": document_data}
        )
        return await self.find_by_id(document_id)
    
    async def delete(self, document_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0
