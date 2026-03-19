from typing import List, Optional
from repositories.concept_repository import ConceptRepository
from fastapi import HTTPException, status


class ConceptService:
    def __init__(self, concept_repository: ConceptRepository):
        self.concept_repository = concept_repository
    
    async def get_all_concepts(self, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.concept_repository.find_all(skip, limit)
    
    async def get_concept_by_id(self, concept_id: str) -> dict:
        concept = await self.concept_repository.find_by_id(concept_id)
        if not concept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Concept not found"
            )
        return concept
    
    async def search_concepts_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.concept_repository.search_by_name(name, skip, limit)
    
    async def create_concept(self, concept_data: dict) -> dict:
        return await self.concept_repository.create(concept_data)
    
    async def update_concept(self, concept_id: str, concept_data: dict) -> dict:
        concept = await self.concept_repository.update(concept_id, concept_data)
        if not concept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Concept not found"
            )
        return concept
    
    async def delete_concept(self, concept_id: str) -> bool:
        result = await self.concept_repository.delete(concept_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Concept not found"
            )
        return result
