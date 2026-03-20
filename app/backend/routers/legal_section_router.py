from fastapi import APIRouter, Depends, Request, Query

from core.security import get_current_user
from dto.legal_section_dto import CreateLegalSectionRequest, UpdateLegalSectionRequest
from utils.response import success_response


def create_legal_section_router_with_state() -> APIRouter:
    router = APIRouter(
        prefix="/api/legal-sections",
        tags=["legal-sections"],
        dependencies=[Depends(get_current_user)],
    )

    @router.get("/")
    async def get_all_sections(
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.legal_section_controller.get_all(skip, limit)
        return success_response(data, message="Legal sections retrieved successfully")

    @router.get("/search")
    async def search_sections(
        title: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.legal_section_controller.search_by_title(title, skip, limit)
        return success_response(data, message="Legal sections retrieved successfully")

    @router.get("/by-so-hieu/{so_hieu}")
    async def get_sections_by_so_hieu(
        so_hieu: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.legal_section_controller.get_by_so_hieu(so_hieu, skip, limit)
        return success_response(data, message="Legal sections retrieved successfully")

    @router.get("/{section_id}")
    async def get_section(section_id: str, req: Request):
        data = await req.app.state.legal_section_controller.get_by_id(section_id)
        return success_response(data, message="Legal section retrieved successfully")

    @router.post("/")
    async def create_section(request: CreateLegalSectionRequest, req: Request):
        data = await req.app.state.legal_section_controller.create(request)
        return success_response(data, message="Legal section created successfully")

    @router.put("/{section_id}")
    async def update_section(section_id: str, request: UpdateLegalSectionRequest, req: Request):
        data = await req.app.state.legal_section_controller.update(section_id, request)
        return success_response(data, message="Legal section updated successfully")

    @router.delete("/{section_id}")
    async def delete_section(section_id: str, req: Request):
        data = await req.app.state.legal_section_controller.delete(section_id)
        return success_response(data, message="Legal section deleted successfully")

    # Association endpoints
    @router.get("/{section_id}/concepts")
    async def get_section_concepts(
        section_id: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.legal_section_controller.get_concepts(section_id, skip, limit)
        return success_response(data, message="Section concepts retrieved successfully")

    @router.get("/{section_id}/relations")
    async def get_section_relations(
        section_id: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.legal_section_controller.get_relations(section_id, skip, limit)
        return success_response(data, message="Section relations retrieved successfully")

    @router.get("/{section_id}/triplets")
    async def get_section_triplets(
        section_id: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.legal_section_controller.get_triplets(section_id, skip, limit)
        return success_response(data, message="Section triplets retrieved successfully")

    return router
