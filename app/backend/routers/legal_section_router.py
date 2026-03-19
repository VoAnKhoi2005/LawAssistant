from fastapi import APIRouter, Request, Query
from controllers.legal_section_controller import LegalSectionController
from dto.legal_section_dto import CreateLegalSectionRequest, UpdateLegalSectionRequest


def create_legal_section_router_with_state() -> APIRouter:
    router = APIRouter(prefix="/api/legal-sections", tags=["legal-sections"])
    
    @router.get("/")
    async def get_all_sections(
        req: Request, 
        skip: int = Query(0, ge=0), 
        limit: int = Query(100, ge=1, le=1000)
    ):
        return await req.app.state.legal_section_controller.get_all(skip, limit)
    
    @router.get("/search")
    async def search_sections(
        title: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
    ):
        return await req.app.state.legal_section_controller.search_by_title(title, skip, limit)
    
    @router.get("/by-so-hieu/{so_hieu}")
    async def get_sections_by_so_hieu(
        so_hieu: str, 
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
    ):
        return await req.app.state.legal_section_controller.get_by_so_hieu(so_hieu, skip, limit)
    
    @router.get("/{section_id}")
    async def get_section(section_id: str, req: Request):
        return await req.app.state.legal_section_controller.get_by_id(section_id)
    
    @router.post("/")
    async def create_section(request: CreateLegalSectionRequest, req: Request):
        return await req.app.state.legal_section_controller.create(request)
    
    @router.put("/{section_id}")
    async def update_section(section_id: str, request: UpdateLegalSectionRequest, req: Request):
        return await req.app.state.legal_section_controller.update(section_id, request)
    
    @router.delete("/{section_id}")
    async def delete_section(section_id: str, req: Request):
        return await req.app.state.legal_section_controller.delete(section_id)
    
    return router
