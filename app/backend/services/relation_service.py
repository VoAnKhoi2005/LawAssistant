from typing import List, Optional
from repositories.relation_repository import RelationRepository
from fastapi import HTTPException, status


class RelationService:
    def __init__(self, relation_repository: RelationRepository):
        self.relation_repository = relation_repository
    
    async def get_all_relations(self, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.relation_repository.find_all(skip, limit)
    
    async def get_relation_by_id(self, relation_id: str) -> dict:
        relation = await self.relation_repository.find_by_id(relation_id)
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relation not found"
            )
        return relation
    
    async def get_relations_by_name(self, relation_name: str, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.relation_repository.find_by_relation_name(relation_name, skip, limit)
    
    async def create_relation(self, relation_data: dict) -> dict:
        return await self.relation_repository.create(relation_data)
    
    async def update_relation(self, relation_id: str, relation_data: dict) -> dict:
        relation = await self.relation_repository.update(relation_id, relation_data)
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relation not found"
            )
        return relation
    
    async def delete_relation(self, relation_id: str) -> bool:
        result = await self.relation_repository.delete(relation_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relation not found"
            )
        return result
