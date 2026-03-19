from typing import List, Optional
from services.triplet_service import TripletService
from dto.triplet_dto import CreateTripletRequest, UpdateTripletRequest, TripletResponse


class TripletController:
    def __init__(self, triplet_service):
        self.triplet_service = triplet_service
    
    async def get_all(self, skip: int = 0, limit: int = 100):
        return await self.triplet_service.get_all_triplets(skip, limit)
    
    async def get_by_id(self, triplet_id: str):
        return await self.triplet_service.get_triplet_by_id(triplet_id)
    
    async def get_by_subject(self, subject_id: str, skip: int = 0, limit: int = 100):
        return await self.triplet_service.get_triplets_by_subject(subject_id, skip, limit)
    
    async def get_by_object(self, object_id: str, skip: int = 0, limit: int = 100):
        return await self.triplet_service.get_triplets_by_object(object_id, skip, limit)
    
    async def create(self, request: CreateTripletRequest):
        triplet_data = request.model_dump(by_alias=True)
        return await self.triplet_service.create_triplet(triplet_data)
    
    async def update(self, triplet_id: str, request: UpdateTripletRequest):
        triplet_data = request.model_dump(by_alias=True, exclude_unset=True)
        return await self.triplet_service.update_triplet(triplet_id, triplet_data)
    
    async def delete(self, triplet_id: str):
        await self.triplet_service.delete_triplet(triplet_id)
        return {"message": "Triplet deleted successfully"}
