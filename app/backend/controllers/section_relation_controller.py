from typing import List, Optional
from services.section_relation_service import SectionRelationService
from dto.section_relation_dto import CreateSectionRelationRequest, UpdateSectionRelationRequest, SectionRelationResponse


class SectionRelationController:
    def __init__(self, section_relation_service: SectionRelationService):
        self.section_relation_service = section_relation_service
    
    async def get_all(self, skip: int = 0, limit: int = 100):
        return await self.section_relation_service.get_all_section_relations(skip, limit)
    
    async def get_by_id(self, relation_id: str):
        return await self.section_relation_service.get_section_relation_by_id(relation_id)
    
    async def get_by_source(self, source: str, skip: int = 0, limit: int = 100):
        return await self.section_relation_service.get_section_relations_by_source(source, skip, limit)
    
    async def get_by_target(self, target: str, skip: int = 0, limit: int = 100):
        return await self.section_relation_service.get_section_relations_by_target(target, skip, limit)
    
    async def get_by_type(self, relation_type: str, skip: int = 0, limit: int = 100):
        return await self.section_relation_service.get_section_relations_by_type(relation_type, skip, limit)
    
    async def create(self, request: CreateSectionRelationRequest):
        relation_data = request.model_dump(by_alias=True)
        return await self.section_relation_service.create_section_relation(relation_data)
    
    async def update(self, relation_id: str, request: UpdateSectionRelationRequest):
        relation_data = request.model_dump(by_alias=True, exclude_unset=True)
        return await self.section_relation_service.update_section_relation(relation_id, relation_data)
    
    async def delete(self, relation_id: str):
        await self.section_relation_service.delete_section_relation(relation_id)
        return {"message": "Section relation deleted successfully"}
