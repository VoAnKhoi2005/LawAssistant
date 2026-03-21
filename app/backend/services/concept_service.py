from typing import List, Optional
from repositories.concept_repository import ConceptRepository
from fastapi import HTTPException, status
from models.concept_model import Concept
from models.common import DocumentRef


class ConceptService:
    def __init__(self, concept_repository: ConceptRepository):
        self.concept_repository = concept_repository
    
    async def get_all_concepts(self, skip: int = 0, limit: int = 100) -> List[Concept]:
        concept_dicts = await self.concept_repository.find_all(skip, limit)
        return [self._dict_to_concept(concept_dict) for concept_dict in concept_dicts]
    
    async def get_concept_by_id(self, concept_id: str) -> Concept:
        concept_dict = await self.concept_repository.find_by_id(concept_id)
        if not concept_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Concept not found"
            )
        return self._dict_to_concept(concept_dict)
    
    async def search_concepts_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Concept]:
        concept_dicts = await self.concept_repository.search_by_name(name, skip, limit)
        return [self._dict_to_concept(concept_dict) for concept_dict in concept_dicts]
    
    async def create_concept(self, concept: Concept) -> Concept:
        return await self.concept_repository.create(concept)
    
    async def update_concept(self, concept_id: str, concept: Concept) -> Concept:
        updated_concept = await self.concept_repository.update(concept_id, concept)
        if not updated_concept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Concept not found"
            )
        return updated_concept
    
    async def delete_concept(self, concept_id: str) -> bool:
        result = await self.concept_repository.delete(concept_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Concept not found"
            )
        return result
    
    async def add_section_to_concept(self, concept_id: str, section_id: str, so_hieu: str) -> Concept:
        concept = await self.get_concept_by_id(concept_id)
        
        # Check if document already exists
        for doc in concept.documents:
            if doc.section_id == section_id and doc.so_hieu == so_hieu:
                return concept
        
        # Add new document reference
        new_doc_ref = DocumentRef(section_id=section_id, so_hieu=so_hieu)
        concept.documents.append(new_doc_ref)
        
        return await self.concept_repository.update(concept_id, concept)
    
    async def remove_section_from_concept(self, concept_id: str, section_id: str) -> Concept:
        concept = await self.get_concept_by_id(concept_id)
        
        # Remove document reference
        concept.documents = [doc for doc in concept.documents if doc.section_id != section_id]
        
        return await self.concept_repository.update(concept_id, concept)
    
    async def get_or_create_concept_by_name(self, name: str) -> Concept:
        """Get existing concept by name or create new one"""
        concept_dict = await self.concept_repository.find_or_create_by_name(name)
        return self._dict_to_concept(concept_dict)
    
    @staticmethod
    def _dict_to_concept(concept_dict: dict) -> Concept:
        # Convert MongoDB dict to Concept model
        concept_dict["_id"] = str(concept_dict["_id"])
        return Concept(**concept_dict)
