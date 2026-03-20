from typing import List, Optional
from repositories.section_relation_repository import SectionRelationRepository
from fastapi import HTTPException, status
from models.section_relation_model import SectionRelation


class SectionRelationService:
    def __init__(self, section_relation_repository: SectionRelationRepository):
        self.section_relation_repository = section_relation_repository
    
    async def get_all_section_relations(self, skip: int = 0, limit: int = 100) -> List[SectionRelation]:
        relation_dicts = await self.section_relation_repository.find_all(skip, limit)
        return [self._dict_to_section_relation(relation_dict) for relation_dict in relation_dicts]
    
    async def get_section_relation_by_id(self, relation_id: str) -> SectionRelation:
        relation_dict = await self.section_relation_repository.find_by_id(relation_id)
        if not relation_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section relation not found"
            )
        return self._dict_to_section_relation(relation_dict)
    
    async def get_section_relations_by_source(self, source: str, skip: int = 0, limit: int = 100) -> List[SectionRelation]:
        relation_dicts = await self.section_relation_repository.find_by_source(source, skip, limit)
        return [self._dict_to_section_relation(relation_dict) for relation_dict in relation_dicts]
    
    async def get_section_relations_by_target(self, target: str, skip: int = 0, limit: int = 100) -> List[SectionRelation]:
        relation_dicts = await self.section_relation_repository.find_by_target(target, skip, limit)
        return [self._dict_to_section_relation(relation_dict) for relation_dict in relation_dicts]
    
    async def get_section_relations_by_type(self, relation_type: str, skip: int = 0, limit: int = 100) -> List[SectionRelation]:
        relation_dicts = await self.section_relation_repository.find_by_type(relation_type, skip, limit)
        return [self._dict_to_section_relation(relation_dict) for relation_dict in relation_dicts]
    
    async def create_section_relation(self, section_relation: SectionRelation) -> SectionRelation:
        return await self.section_relation_repository.create(section_relation)
    
    async def update_section_relation(self, relation_id: str, section_relation: SectionRelation) -> SectionRelation:
        updated_relation = await self.section_relation_repository.update(relation_id, section_relation)
        if not updated_relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section relation not found"
            )
        return updated_relation
    
    async def delete_section_relation(self, relation_id: str) -> bool:
        result = await self.section_relation_repository.delete(relation_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section relation not found"
            )
        return result

    @staticmethod
    def _dict_to_section_relation(relation_dict: dict) -> SectionRelation:
        # Convert MongoDB dict to SectionRelation model
        relation_dict["_id"] = str(relation_dict["_id"])
        return SectionRelation(**relation_dict)
