from typing import List, Optional
from repositories.section_relation_repository import SectionRelationRepository
from fastapi import HTTPException, status


class SectionRelationService:
    def __init__(self, section_relation_repository: SectionRelationRepository):
        self.section_relation_repository = section_relation_repository
    
    async def get_all_section_relations(self, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.section_relation_repository.find_all(skip, limit)
    
    async def get_section_relation_by_id(self, relation_id: str) -> dict:
        relation = await self.section_relation_repository.find_by_id(relation_id)
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section relation not found"
            )
        return relation
    
    async def get_section_relations_by_source(self, source: str, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.section_relation_repository.find_by_source(source, skip, limit)
    
    async def get_section_relations_by_target(self, target: str, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.section_relation_repository.find_by_target(target, skip, limit)
    
    async def get_section_relations_by_type(self, relation_type: str, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.section_relation_repository.find_by_type(relation_type, skip, limit)
    
    async def create_section_relation(self, relation_data: dict) -> dict:
        return await self.section_relation_repository.create(relation_data)
    
    async def update_section_relation(self, relation_id: str, relation_data: dict) -> dict:
        relation = await self.section_relation_repository.update(relation_id, relation_data)
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section relation not found"
            )
        return relation
    
    async def delete_section_relation(self, relation_id: str) -> bool:
        result = await self.section_relation_repository.delete(relation_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section relation not found"
            )
        return result
