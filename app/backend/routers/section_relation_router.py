from fastapi import APIRouter, Request, Query
from controllers.section_relation_controller import SectionRelationController
from dto.section_relation_dto import CreateSectionRelationRequest, UpdateSectionRelationRequest


def create_section_relation_router_with_state() -> APIRouter:
    router = APIRouter(prefix="/api/section-relations", tags=["section-relations"])
    
    @router.get("/")
    async def get_all_section_relations(
        req: Request, 
        skip: int = Query(0, ge=0), 
        limit: int = Query(100, ge=1, le=1000)
    ):
        return await req.app.state.section_relation_controller.get_all(skip, limit)
    
    @router.get("/by-source/{source}")
    async def get_section_relations_by_source(
        source: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
    ):
        return await req.app.state.section_relation_controller.get_by_source(source, skip, limit)
    
    @router.get("/by-target/{target}")
    async def get_section_relations_by_target(
        target: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
    ):
        return await req.app.state.section_relation_controller.get_by_target(target, skip, limit)
    
    @router.get("/by-type/{relation_type}")
    async def get_section_relations_by_type(
        relation_type: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
    ):
        return await req.app.state.section_relation_controller.get_by_type(relation_type, skip, limit)
    
    @router.get("/{relation_id}")
    async def get_section_relation(relation_id: str, req: Request):
        return await req.app.state.section_relation_controller.get_by_id(relation_id)
    
    @router.post("/")
    async def create_section_relation(request: CreateSectionRelationRequest, req: Request):
        return await req.app.state.section_relation_controller.create(request)
    
    @router.put("/{relation_id}")
    async def update_section_relation(relation_id: str, request: UpdateSectionRelationRequest, req: Request):
        return await req.app.state.section_relation_controller.update(relation_id, request)
    
    @router.delete("/{relation_id}")
    async def delete_section_relation(relation_id: str, req: Request):
        return await req.app.state.section_relation_controller.delete(relation_id)
    
    return router
