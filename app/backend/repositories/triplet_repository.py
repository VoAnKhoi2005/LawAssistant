from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId

from models.triplet_model import Triplet


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
        cursor = self.collection.find({"subject_id": subject_id}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_by_object(self, object_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find({"object_id": object_id}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def create(self, triplet: Triplet) -> Triplet:
        triplet_dict = triplet.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(triplet_dict)
        triplet_dict["_id"] = result.inserted_id
        return Triplet(**triplet_dict)
    
    async def update(self, triplet_id: str, triplet: Triplet) -> Optional[Triplet]:
        triplet_dict = triplet.model_dump(by_alias=True, exclude={"id"})
        await self.collection.update_one(
            {"_id": ObjectId(triplet_id)},
            {"$set": triplet_dict}
        )
        updated_dict = await self.find_by_id(triplet_id)
        if updated_dict:
            updated_dict["_id"] = str(updated_dict["_id"])
            return Triplet(**updated_dict)
        return None
    
    async def delete(self, triplet_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(triplet_id)})
        return result.deleted_count > 0
    
    async def create_many(self, triplets: List[Triplet]) -> List[Triplet]:
        """Batch create multiple triplets"""
        triplet_dicts = [triplet.model_dump(by_alias=True, exclude={"id"}) for triplet in triplets]
        result = await self.collection.insert_many(triplet_dicts)
        
        created_triplets = []
        for idx, inserted_id in enumerate(result.inserted_ids):
            triplet_dicts[idx]["_id"] = str(inserted_id)
            created_triplets.append(Triplet(**triplet_dicts[idx]))
        
        return created_triplets
    
    async def find_by_document(self, document_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """Find triplets associated with a specific document"""
        cursor = self.collection.find(
            {"documents.section_id": document_id}
        ).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
