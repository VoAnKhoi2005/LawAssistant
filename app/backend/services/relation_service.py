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
    
    async def add_section_to_relation(self, relation_id: str, section_id: str, so_hieu: str) -> dict:
        relation = await self.get_relation_by_id(relation_id)
        
        # Check if document already exists
        documents = relation.get("documents", [])
        for doc in documents:
            if doc.get("section_id") == section_id and doc.get("so_hieu") == so_hieu:
                return relation
        
        # Add new document reference
        documents.append({"section_id": section_id, "so_hieu": so_hieu})
        
        from bson import ObjectId
        await self.relation_repository.collection.update_one(
            {"_id": ObjectId(relation_id)},
            {"$set": {"documents": documents}}
        )
        
        return await self.get_relation_by_id(relation_id)
    
    async def remove_section_from_relation(self, relation_id: str, section_id: str) -> dict:
        relation = await self.get_relation_by_id(relation_id)
        
        # Remove document reference
        documents = relation.get("documents", [])
        documents = [doc for doc in documents if doc.get("section_id") != section_id]
        
        from bson import ObjectId
        await self.relation_repository.collection.update_one(
            {"_id": ObjectId(relation_id)},
            {"$set": {"documents": documents}}
        )
        
        return await self.get_relation_by_id(relation_id)
