from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId

from models.concept_model import Concept


class ConceptRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["concepts"]
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find().skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_by_id(self, concept_id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": ObjectId(concept_id)})
    
    async def find_by_name(self, name: str) -> Optional[dict]:
        return await self.collection.find_one({"name": name})
    
    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find({"name": {"$regex": name, "$options": "i"}}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def create(self, concept: Concept) -> Concept:
        concept_dict = concept.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(concept_dict)
        concept_dict["_id"] = result.inserted_id
        return Concept(**concept_dict)
    
    async def update(self, concept_id: str, concept: Concept) -> Optional[Concept]:
        concept_dict = concept.model_dump(by_alias=True, exclude={"id"})
        await self.collection.update_one(
            {"_id": ObjectId(concept_id)},
            {"$set": concept_dict}
        )
        updated_dict = await self.find_by_id(concept_id)
        if updated_dict:
            updated_dict["_id"] = str(updated_dict["_id"])
            return Concept(**updated_dict)
        return None
    
    async def delete(self, concept_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(concept_id)})
        return result.deleted_count > 0
