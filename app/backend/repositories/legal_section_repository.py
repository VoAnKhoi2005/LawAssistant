from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List


class LegalSectionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["legal_sections"]
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find().skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_by_id(self, section_id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": section_id})
    
    async def find_by_so_hieu(self, so_hieu: str, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find({"so_hieu": so_hieu}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def search_by_title(self, title: str, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find({"title": {"$regex": title, "$options": "i"}}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def create(self, section_data: dict) -> dict:
        result = await self.collection.insert_one(section_data)
        return section_data
    
    async def update(self, section_id: str, section_data: dict) -> Optional[dict]:
        await self.collection.update_one(
            {"_id": section_id},
            {"$set": section_data}
        )
        return await self.find_by_id(section_id)
    
    async def delete(self, section_id: str) -> bool:
        result = await self.collection.delete_one({"_id": section_id})
        return result.deleted_count > 0
