from typing import List, Optional
from services.concept_service import ConceptService
from dto.concept_dto import CreateConceptRequest, UpdateConceptRequest, ConceptResponse
from pydantic import BaseModel


class AddSectionToConceptRequest(BaseModel):
    section_id: str
    so_hieu: str


class ConceptController:
    def __init__(self, concept_service: ConceptService):
        self.concept_service = concept_service
    
    async def get_all(self, skip: int = 0, limit: int = 100):
        return await self.concept_service.get_all_concepts(skip, limit)
    
    async def get_by_id(self, concept_id: str):
        return await self.concept_service.get_concept_by_id(concept_id)
    
    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100):
        return await self.concept_service.search_concepts_by_name(name, skip, limit)
    
    async def create(self, request: CreateConceptRequest):
        concept_data = request.model_dump(by_alias=True)
        return await self.concept_service.create_concept(concept_data)
    
    async def update(self, concept_id: str, request: UpdateConceptRequest):
        concept_data = request.model_dump(by_alias=True, exclude_unset=True)
        return await self.concept_service.update_concept(concept_id, concept_data)
    
    async def delete(self, concept_id: str):
        await self.concept_service.delete_concept(concept_id)
        return {"message": "Concept deleted successfully"}
    
    async def add_section(self, concept_id: str, request: AddSectionToConceptRequest):
        return await self.concept_service.add_section_to_concept(
            concept_id, request.section_id, request.so_hieu
        )
    
    async def remove_section(self, concept_id: str, section_id: str):
        return await self.concept_service.remove_section_from_concept(concept_id, section_id)
