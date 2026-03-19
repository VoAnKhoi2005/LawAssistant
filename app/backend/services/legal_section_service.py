from typing import List, Optional
from repositories.legal_section_repository import LegalSectionRepository
from fastapi import HTTPException, status


class LegalSectionService:
    def __init__(self, legal_section_repository: LegalSectionRepository):
        self.legal_section_repository = legal_section_repository
    
    async def get_all_sections(self, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.legal_section_repository.find_all(skip, limit)
    
    async def get_section_by_id(self, section_id: str) -> dict:
        section = await self.legal_section_repository.find_by_id(section_id)
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Legal section not found"
            )
        return section
    
    async def get_sections_by_so_hieu(self, so_hieu: str, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.legal_section_repository.find_by_so_hieu(so_hieu, skip, limit)
    
    async def search_sections_by_title(self, title: str, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.legal_section_repository.search_by_title(title, skip, limit)
    
    async def create_section(self, section_data: dict) -> dict:
        return await self.legal_section_repository.create(section_data)
    
    async def update_section(self, section_id: str, section_data: dict) -> dict:
        section = await self.legal_section_repository.update(section_id, section_data)
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Legal section not found"
            )
        return section
    
    async def delete_section(self, section_id: str) -> bool:
        result = await self.legal_section_repository.delete(section_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Legal section not found"
            )
        return result
