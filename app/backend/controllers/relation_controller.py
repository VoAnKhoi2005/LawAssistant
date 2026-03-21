from typing import List, Optional
from services.relation_service import RelationService
from dto.relation_dto import CreateRelationRequest, UpdateRelationRequest, RelationResponse
from pydantic import BaseModel


class AddSectionToRelationRequest(BaseModel):
    section_id: str
    so_hieu: str


class RelationController:
    def __init__(self, relation_service: RelationService):
        self.relation_service = relation_service
    
    async def get_all(self, skip: int = 0, limit: int = 100):
        return await self.relation_service.get_all_relations(skip, limit)
    
    async def get_by_id(self, relation_id: str):
        return await self.relation_service.get_relation_by_id(relation_id)
    
    async def get_by_name(self, relation_name: str, skip: int = 0, limit: int = 100):
        return await self.relation_service.get_relations_by_name(relation_name, skip, limit)
    
    async def create(self, request: CreateRelationRequest):
        relation_data = request.model_dump(by_alias=True)
        return await self.relation_service.create_relation(relation_data)
    
    async def update(self, relation_id: str, request: UpdateRelationRequest):
        relation_data = request.model_dump(by_alias=True, exclude_unset=True)
        return await self.relation_service.update_relation(relation_id, relation_data)
    
    async def delete(self, relation_id: str):
        await self.relation_service.delete_relation(relation_id)
        return {"message": "Relation deleted successfully"}
    
    async def add_section(self, relation_id: str, request: AddSectionToRelationRequest):
        return await self.relation_service.add_section_to_relation(
            relation_id, request.section_id, request.so_hieu
        )
    
    async def remove_section(self, relation_id: str, section_id: str):
        return await self.relation_service.remove_section_from_relation(relation_id, section_id)
