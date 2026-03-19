from fastapi import APIRouter, Depends, Request, Query

from controllers.section_relation_controller import SectionRelationController
from core.security import get_current_user
from dto.section_relation_dto import CreateSectionRelationRequest, UpdateSectionRelationRequest
from utils.response import success_response


def create_section_relation_router_with_state() -> APIRouter:
    router = APIRouter(
        prefix="/api/section-relations",
        tags=["section-relations"],
        dependencies=[Depends(get_current_user)],
    )

    @router.get("/")
    async def get_all_section_relations(
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.section_relation_controller.get_all(skip, limit)
        return success_response(data, message="Section relations retrieved successfully")

    @router.get("/by-source/{source}")
    async def get_section_relations_by_source(
        source: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.section_relation_controller.get_by_source(source, skip, limit)
        return success_response(data, message="Section relations retrieved successfully")

    @router.get("/by-target/{target}")
    async def get_section_relations_by_target(
        target: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.section_relation_controller.get_by_target(target, skip, limit)
        return success_response(data, message="Section relations retrieved successfully")

    @router.get("/by-type/{relation_type}")
    async def get_section_relations_by_type(
        relation_type: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.section_relation_controller.get_by_type(relation_type, skip, limit)
        return success_response(data, message="Section relations retrieved successfully")

    @router.get("/{relation_id}")
    async def get_section_relation(relation_id: str, req: Request):
        data = await req.app.state.section_relation_controller.get_by_id(relation_id)
        return success_response(data, message="Section relation retrieved successfully")

    @router.post("/")
    async def create_section_relation(request: CreateSectionRelationRequest, req: Request):
        data = await req.app.state.section_relation_controller.create(request)
        return success_response(data, message="Section relation created successfully")

    @router.put("/{relation_id}")
    async def update_section_relation(
        relation_id: str, request: UpdateSectionRelationRequest, req: Request
    ):
        data = await req.app.state.section_relation_controller.update(relation_id, request)
        return success_response(data, message="Section relation updated successfully")

    @router.delete("/{relation_id}")
    async def delete_section_relation(relation_id: str, req: Request):
        data = await req.app.state.section_relation_controller.delete(relation_id)
        return success_response(data, message="Section relation deleted successfully")

    return router
