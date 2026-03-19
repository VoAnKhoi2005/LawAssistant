from typing import List, Optional
from repositories.triplet_repository import TripletRepository
from fastapi import HTTPException, status


class TripletService:
    def __init__(self, triplet_repository: TripletRepository):
        self.triplet_repository = triplet_repository
    
    async def get_all_triplets(self, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.triplet_repository.find_all(skip, limit)
    
    async def get_triplet_by_id(self, triplet_id: str) -> dict:
        triplet = await self.triplet_repository.find_by_id(triplet_id)
        if not triplet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Triplet not found"
            )
        return triplet
    
    async def get_triplets_by_subject(self, subject_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.triplet_repository.find_by_subject(subject_id, skip, limit)
    
    async def get_triplets_by_object(self, object_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.triplet_repository.find_by_object(object_id, skip, limit)
    
    async def create_triplet(self, triplet_data: dict) -> dict:
        return await self.triplet_repository.create(triplet_data)
    
    async def update_triplet(self, triplet_id: str, triplet_data: dict) -> dict:
        triplet = await self.triplet_repository.update(triplet_id, triplet_data)
        if not triplet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Triplet not found"
            )
        return triplet
    
    async def delete_triplet(self, triplet_id: str) -> bool:
        result = await self.triplet_repository.delete(triplet_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Triplet not found"
            )
        return result
    
    async def add_section_to_triplet(self, triplet_id: str, section_id: str, so_hieu: str) -> dict:
        triplet = await self.get_triplet_by_id(triplet_id)
        
        # Check if document already exists
        documents = triplet.get("documents", [])
        for doc in documents:
            if doc.get("section_id") == section_id and doc.get("so_hieu") == so_hieu:
                return triplet
        
        # Add new document reference
        documents.append({"section_id": section_id, "so_hieu": so_hieu})
        
        from bson import ObjectId
        await self.triplet_repository.collection.update_one(
            {"_id": ObjectId(triplet_id)},
            {"$set": {"documents": documents}}
        )
        
        return await self.get_triplet_by_id(triplet_id)
    
    async def remove_section_from_triplet(self, triplet_id: str, section_id: str) -> dict:
        triplet = await self.get_triplet_by_id(triplet_id)
        
        # Remove document reference
        documents = triplet.get("documents", [])
        documents = [doc for doc in documents if doc.get("section_id") != section_id]
        
        from bson import ObjectId
        await self.triplet_repository.collection.update_one(
            {"_id": ObjectId(triplet_id)},
            {"$set": {"documents": documents}}
        )
        
        return await self.get_triplet_by_id(triplet_id)
