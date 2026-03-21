from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId

from models.legal_section_model import LegalSection


class LegalSectionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["legal_sections"]
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find().skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_by_id(self, section_id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": ObjectId(section_id)})
    
    async def find_by_so_hieu(self, so_hieu: str, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find({"so_hieu": so_hieu}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def search_by_title(self, title: str, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find({"title": {"$regex": title, "$options": "i"}}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def create(self, section: LegalSection) -> LegalSection:
        section_dict = section.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(section_dict)
        section_dict["_id"] = result.inserted_id
        return LegalSection(**section_dict)
    
    async def update(self, section_id: str, section: LegalSection) -> Optional[LegalSection]:
        section_dict = section.model_dump(by_alias=True, exclude={"id"})
        await self.collection.update_one(
            {"_id": ObjectId(section_id)},
            {"$set": section_dict}
        )
        updated_dict = await self.find_by_id(section_id)
        if updated_dict:
            updated_dict["_id"] = str(updated_dict["_id"])
            return LegalSection(**updated_dict)
        return None
    
    async def delete(self, section_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(section_id)})
        return result.deleted_count > 0
