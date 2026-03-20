from typing import List, Optional
from repositories.triplet_repository import TripletRepository
from fastapi import HTTPException, status
from models.triplet_model import Triplet
from models.common import DocumentRef


class TripletService:
    def __init__(self, triplet_repository: TripletRepository):
        self.triplet_repository = triplet_repository
    
    async def get_all_triplets(self, skip: int = 0, limit: int = 100) -> List[Triplet]:
        triplet_dicts = await self.triplet_repository.find_all(skip, limit)
        return [self._dict_to_triplet(triplet_dict) for triplet_dict in triplet_dicts]
    
    async def get_triplet_by_id(self, triplet_id: str) -> Triplet:
        triplet_dict = await self.triplet_repository.find_by_id(triplet_id)
        if not triplet_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Triplet not found"
            )
        return self._dict_to_triplet(triplet_dict)
    
    async def get_triplets_by_subject(self, subject_id: str, skip: int = 0, limit: int = 100) -> List[Triplet]:
        triplet_dicts = await self.triplet_repository.find_by_subject(subject_id, skip, limit)
        return [self._dict_to_triplet(triplet_dict) for triplet_dict in triplet_dicts]
    
    async def get_triplets_by_object(self, object_id: str, skip: int = 0, limit: int = 100) -> List[Triplet]:
        triplet_dicts = await self.triplet_repository.find_by_object(object_id, skip, limit)
        return [self._dict_to_triplet(triplet_dict) for triplet_dict in triplet_dicts]
    
    async def create_triplet(self, triplet: Triplet) -> Triplet:
        return await self.triplet_repository.create(triplet)
    
    async def update_triplet(self, triplet_id: str, triplet: Triplet) -> Triplet:
        updated_triplet = await self.triplet_repository.update(triplet_id, triplet)
        if not updated_triplet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Triplet not found"
            )
        return updated_triplet
    
    async def delete_triplet(self, triplet_id: str) -> bool:
        result = await self.triplet_repository.delete(triplet_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Triplet not found"
            )
        return result
    
    async def add_section_to_triplet(self, triplet_id: str, section_id: str, so_hieu: str) -> Triplet:
        triplet = await self.get_triplet_by_id(triplet_id)
        
        # Check if document already exists
        for doc in triplet.documents:
            if doc.section_id == section_id and doc.so_hieu == so_hieu:
                return triplet
        
        # Add new document reference
        new_doc_ref = DocumentRef(section_id=section_id, so_hieu=so_hieu)
        triplet.documents.append(new_doc_ref)
        
        return await self.triplet_repository.update(triplet_id, triplet)
    
    async def remove_section_from_triplet(self, triplet_id: str, section_id: str) -> Triplet:
        triplet = await self.get_triplet_by_id(triplet_id)
        
        # Remove document reference
        triplet.documents = [doc for doc in triplet.documents if doc.section_id != section_id]
        
        return await self.triplet_repository.update(triplet_id, triplet)

    @staticmethod
    def _dict_to_triplet(triplet_dict: dict) -> Triplet:
        # Convert MongoDB dict to Triplet model
        triplet_dict["_id"] = str(triplet_dict["_id"])
        return Triplet(**triplet_dict)
