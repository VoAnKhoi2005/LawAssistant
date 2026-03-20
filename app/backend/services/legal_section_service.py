from typing import List, Optional
from repositories.legal_section_repository import LegalSectionRepository
from repositories.concept_repository import ConceptRepository
from repositories.relation_repository import RelationRepository
from repositories.triplet_repository import TripletRepository
from fastapi import HTTPException, status
from models.legal_section_model import LegalSection


class LegalSectionService:
    def __init__(
        self, 
        legal_section_repository: LegalSectionRepository,
        concept_repository: ConceptRepository = None,
        relation_repository: RelationRepository = None,
        triplet_repository: TripletRepository = None
    ):
        self.legal_section_repository = legal_section_repository
        self.concept_repository = concept_repository
        self.relation_repository = relation_repository
        self.triplet_repository = triplet_repository
    
    async def get_all_sections(self, skip: int = 0, limit: int = 100) -> List[LegalSection]:
        section_dicts = await self.legal_section_repository.find_all(skip, limit)
        return [self._dict_to_legal_section(section_dict) for section_dict in section_dicts]
    
    async def get_section_by_id(self, section_id: str) -> LegalSection:
        section_dict = await self.legal_section_repository.find_by_id(section_id)
        if not section_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Legal section not found"
            )
        return self._dict_to_legal_section(section_dict)
    
    async def get_sections_by_so_hieu(self, so_hieu: str, skip: int = 0, limit: int = 100) -> List[LegalSection]:
        section_dicts = await self.legal_section_repository.find_by_so_hieu(so_hieu, skip, limit)
        return [self._dict_to_legal_section(section_dict) for section_dict in section_dicts]
    
    async def search_sections_by_title(self, title: str, skip: int = 0, limit: int = 100) -> List[LegalSection]:
        section_dicts = await self.legal_section_repository.search_by_title(title, skip, limit)
        return [self._dict_to_legal_section(section_dict) for section_dict in section_dicts]
    
    async def create_section(self, section: LegalSection) -> LegalSection:
        return await self.legal_section_repository.create(section)
    
    async def update_section(self, section_id: str, section: LegalSection) -> LegalSection:
        updated_section = await self.legal_section_repository.update(section_id, section)
        if not updated_section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Legal section not found"
            )
        return updated_section

    async def delete_section(self, section_id: str) -> bool:
        result = await self.legal_section_repository.delete(section_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Legal section not found"
            )
        return result

    @staticmethod
    def _dict_to_legal_section(section_dict: dict) -> LegalSection:
        # Convert MongoDB dict to LegalSection model
        section_dict["_id"] = str(section_dict["_id"])
        return LegalSection(**section_dict)
    
    async def delete_section(self, section_id: str) -> bool:
        result = await self.legal_section_repository.delete(section_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Legal section not found"
            )
        return result
    
    # Association methods
    async def get_section_concepts(self, section_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        # Find concepts in the documents field that reference this section
        if not self.concept_repository:
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Concept repository not available")
        
        # Query concepts where documents contain this section_id
        from bson import ObjectId
        concepts = await self.concept_repository.collection.find({
            "documents.section_id": section_id
        }).skip(skip).limit(limit).to_list(length=limit)
        return concepts
    
    async def get_section_relations(self, section_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        if not self.relation_repository:
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Relation repository not available")
        
        relations = await self.relation_repository.collection.find({
            "documents.section_id": section_id
        }).skip(skip).limit(limit).to_list(length=limit)
        return relations
    
    async def get_section_triplets(self, section_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        if not self.triplet_repository:
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Triplet repository not available")
        
        # Return triplets where this section is subject or object
        from bson import ObjectId
        triplets = await self.triplet_repository.collection.find({
            "$or": [
                {"subject.id": section_id},
                {"object.id": section_id}
            ]
        }).skip(skip).limit(limit).to_list(length=limit)
        return triplets

    @staticmethod
    def _dict_to_legal_section(section_dict: dict) -> LegalSection:
        # Convert MongoDB dict to LegalSection model
        section_dict["_id"] = str(section_dict["_id"])
        return LegalSection(**section_dict)
