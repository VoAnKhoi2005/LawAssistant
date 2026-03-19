from typing import List, Optional
from services.legal_section_service import LegalSectionService
from dto.legal_section_dto import CreateLegalSectionRequest, UpdateLegalSectionRequest, LegalSectionResponse


class LegalSectionController:
    def __init__(self, legal_section_service: LegalSectionService):
        self.legal_section_service = legal_section_service
    
    async def get_all(self, skip: int = 0, limit: int = 100):
        return await self.legal_section_service.get_all_sections(skip, limit)
    
    async def get_by_id(self, section_id: str):
        return await self.legal_section_service.get_section_by_id(section_id)
    
    async def get_by_so_hieu(self, so_hieu: str, skip: int = 0, limit: int = 100):
        return await self.legal_section_service.get_sections_by_so_hieu(so_hieu, skip, limit)
    
    async def search_by_title(self, title: str, skip: int = 0, limit: int = 100):
        return await self.legal_section_service.search_sections_by_title(title, skip, limit)
    
    async def create(self, request: CreateLegalSectionRequest):
        section_data = request.model_dump(by_alias=True)
        section_data["_id"] = section_data.pop("id")
        return await self.legal_section_service.create_section(section_data)
    
    async def update(self, section_id: str, request: UpdateLegalSectionRequest):
        section_data = request.model_dump(by_alias=True, exclude_unset=True)
        return await self.legal_section_service.update_section(section_id, section_data)
    
    async def delete(self, section_id: str):
        await self.legal_section_service.delete_section(section_id)
        return {"message": "Legal section deleted successfully"}
