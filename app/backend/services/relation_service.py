from typing import List, Optional
from repositories.relation_repository import RelationRepository
from fastapi import HTTPException, status
from models.relation_model import Relation
from models.common import DocumentRef


class RelationService:
    def __init__(self, relation_repository: RelationRepository):
        self.relation_repository = relation_repository
    
    async def get_all_relations(self, skip: int = 0, limit: int = 100) -> List[Relation]:
        relation_dicts = await self.relation_repository.find_all(skip, limit)
        return [self._dict_to_relation(relation_dict) for relation_dict in relation_dicts]
    
    async def get_relation_by_id(self, relation_id: str) -> Relation:
        relation_dict = await self.relation_repository.find_by_id(relation_id)
        if not relation_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relation not found"
            )
        return self._dict_to_relation(relation_dict)
    
    async def get_relations_by_name(self, relation_name: str, skip: int = 0, limit: int = 100) -> List[Relation]:
        relation_dicts = await self.relation_repository.find_by_relation_name(relation_name, skip, limit)
        return [self._dict_to_relation(relation_dict) for relation_dict in relation_dicts]
    
    async def create_relation(self, relation: Relation) -> Relation:
        return await self.relation_repository.create(relation)
    
    async def update_relation(self, relation_id: str, relation: Relation) -> Relation:
        updated_relation = await self.relation_repository.update(relation_id, relation)
        if not updated_relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relation not found"
            )
        return updated_relation
    
    async def delete_relation(self, relation_id: str) -> bool:
        result = await self.relation_repository.delete(relation_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relation not found"
            )
        return result
    
    async def add_section_to_relation(self, relation_id: str, section_id: str, so_hieu: str) -> Relation:
        relation = await self.get_relation_by_id(relation_id)
        
        # Check if document already exists
        for doc in relation.documents:
            if doc.section_id == section_id and doc.so_hieu == so_hieu:
                return relation
        
        # Add new document reference
        new_doc_ref = DocumentRef(section_id=section_id, so_hieu=so_hieu)
        relation.documents.append(new_doc_ref)
        
        return await self.relation_repository.update(relation_id, relation)
    
    async def remove_section_from_relation(self, relation_id: str, section_id: str) -> Relation:
        relation = await self.get_relation_by_id(relation_id)
        
        # Remove document reference
        relation.documents = [doc for doc in relation.documents if doc.section_id != section_id]
        
        return await self.relation_repository.update(relation_id, relation)

    @staticmethod
    def _dict_to_relation(relation_dict: dict) -> Relation:
        # Convert MongoDB dict to Relation model
        relation_dict["_id"] = str(relation_dict["_id"])
        return Relation(**relation_dict)
