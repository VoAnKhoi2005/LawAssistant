from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId
from pymongo import ReturnDocument

from models.relation_model import Relation
from models.common import DocumentRef


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
        cursor = self.collection.find({
            "$or": [
                {"name": relation_name},
                {"relation_name": relation_name},
            ]
        }).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def create(self, relation: Relation) -> Relation:
        relation_dict = relation.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(relation_dict)
        relation_dict["_id"] = result.inserted_id
        return Relation(**relation_dict)
    
    async def update(self, relation_id: str, relation: Relation) -> Optional[Relation]:
        relation_dict = relation.model_dump(by_alias=True, exclude={"id"})
        await self.collection.update_one(
            {"_id": ObjectId(relation_id)},
            {"$set": relation_dict}
        )
        updated_dict = await self.find_by_id(relation_id)
        if updated_dict:
            updated_dict["_id"] = str(updated_dict["_id"])
            return Relation(**updated_dict)
        return None
    
    async def delete(self, relation_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(relation_id)})
        return result.deleted_count > 0
    
    async def find_or_create_by_name(self, relation_name: str, subject_name: str = "", object_name: str = "") -> dict:
        """Find relation by name or create if not exists"""
        existing_list = await self.find_by_relation_name(relation_name)
        if existing_list and len(existing_list) > 0:
            return existing_list[0]
        
        relation = Relation(
            name=relation_name,
            subject_name=subject_name,
            object_name=object_name
        )
        created = await self.create(relation)
        relation_dict = created.model_dump(by_alias=True)
        relation_dict["_id"] = created.id
        return relation_dict

    async def find_or_create_with_document(self, relation_name: str, document_ref: DocumentRef) -> str:
        relation_dict = await self.collection.find_one_and_update(
            {
                "$or": [
                    {"name": relation_name},
                    {"relation_name": relation_name},
                ]
            },
            {
                "$addToSet": {"documents": document_ref.model_dump()},
                "$setOnInsert": {
                    "name": relation_name,
                    "description": None,
                    "synonym": [],
                },
                "$unset": {
                    "relation_name": "",
                },
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return str(relation_dict["_id"])
