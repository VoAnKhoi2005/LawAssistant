from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId

from models.section_relation_model import SectionRelation


class SectionRelationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["section_relations"]
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find().skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_by_id(self, relation_id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": ObjectId(relation_id)})
    
    async def find_by_source(self, source: str, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find({"source": source}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_by_target(self, target: str, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find({"target": target}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_by_type(self, relation_type: str, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find({"type": relation_type}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def create(self, section_relation: SectionRelation) -> SectionRelation:
        relation_dict = section_relation.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(relation_dict)
        relation_dict["_id"] = result.inserted_id
        return SectionRelation(**relation_dict)
    
    async def update(self, relation_id: str, section_relation: SectionRelation) -> Optional[SectionRelation]:
        relation_dict = section_relation.model_dump(by_alias=True, exclude={"id"})
        await self.collection.update_one(
            {"_id": ObjectId(relation_id)},
            {"$set": relation_dict}
        )
        updated_dict = await self.find_by_id(relation_id)
        if updated_dict:
            updated_dict["_id"] = str(updated_dict["_id"])
            return SectionRelation(**updated_dict)
        return None
    
    async def delete(self, relation_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(relation_id)})
        return result.deleted_count > 0
