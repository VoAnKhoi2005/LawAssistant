from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId
from datetime import datetime

from models.uploaded_file_model import UploadedFile


class UploadFileRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["uploaded_files"]
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find().skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_by_id(self, file_id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": ObjectId(file_id)})
    
    async def find_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find({"user_id": user_id}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find({"status": status}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def create(self, uploaded_file: UploadedFile) -> UploadedFile:
        file_dict = uploaded_file.model_dump(by_alias=True, exclude={"id"})
        file_dict["created_at"] = datetime.utcnow()
        file_dict["updated_at"] = datetime.utcnow()
        result = await self.collection.insert_one(file_dict)
        file_dict["_id"] = result.inserted_id
        return UploadedFile(**file_dict)
    
    async def create_from_dict(self, file_data: dict) -> dict:
        """Legacy method for dict-based creation"""
        file_data["created_at"] = datetime.utcnow()
        file_data["updated_at"] = datetime.utcnow()
        result = await self.collection.insert_one(file_data)
        file_data["_id"] = str(result.inserted_id)
        return file_data
    
    async def update(self, file_id: str, uploaded_file: UploadedFile) -> Optional[UploadedFile]:
        file_dict = uploaded_file.model_dump(by_alias=True, exclude={"id"})
        file_dict["updated_at"] = datetime.utcnow()
        await self.collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": file_dict}
        )
        updated_dict = await self.find_by_id(file_id)
        if updated_dict:
            updated_dict["_id"] = str(updated_dict["_id"])
            return UploadedFile(**updated_dict)
        return None
    
    async def update_status(self, file_id: str, status: str, error: Optional[str] = None) -> Optional[dict]:
        update_data = {"status": status, "updated_at": datetime.utcnow()}
        if error:
            update_data["error"] = error
        
        await self.collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": update_data}
        )
        return await self.find_by_id(file_id)
    
    async def delete(self, file_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(file_id)})
        return result.deleted_count > 0