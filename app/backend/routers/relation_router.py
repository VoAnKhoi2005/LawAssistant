from fastapi import APIRouter, Depends, Request, Query

from controllers.relation_controller import AddSectionToRelationRequest
from core.security import get_current_user
from dto.relation_dto import CreateRelationRequest, UpdateRelationRequest
from utils.response import success_response


def create_relation_router_with_state() -> APIRouter:
    router = APIRouter(
        prefix="/api/relations",
        tags=["relations"],
        dependencies=[Depends(get_current_user)],
    )

    @router.get("/")
    async def get_all_relations(
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.relation_controller.get_all(skip, limit)
        return success_response(data, message="Relations retrieved successfully")

    @router.get("/by-name/{relation_name}")
    async def get_relations_by_name(
        relation_name: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.relation_controller.get_by_name(relation_name, skip, limit)
        return success_response(data, message="Relations retrieved successfully")

    @router.get("/{relation_id}")
    async def get_relation(relation_id: str, req: Request):
        data = await req.app.state.relation_controller.get_by_id(relation_id)
        return success_response(data, message="Relation retrieved successfully")

    @router.post("/")
    async def create_relation(request: CreateRelationRequest, req: Request):
        data = await req.app.state.relation_controller.create(request)
        return success_response(data, message="Relation created successfully")

    @router.put("/{relation_id}")
    async def update_relation(relation_id: str, request: UpdateRelationRequest, req: Request):
        data = await req.app.state.relation_controller.update(relation_id, request)
        return success_response(data, message="Relation updated successfully")

    @router.delete("/{relation_id}")
    async def delete_relation(relation_id: str, req: Request):
        data = await req.app.state.relation_controller.delete(relation_id)
        return success_response(data, message="Relation deleted successfully")

    # Section association endpoints
    @router.post("/{relation_id}/sections")
    async def add_section_to_relation(
        relation_id: str, request: AddSectionToRelationRequest, req: Request
    ):
        data = await req.app.state.relation_controller.add_section(relation_id, request)
        return success_response(data, message="Section linked to relation successfully")

    @router.delete("/{relation_id}/sections/{section_id}")
    async def remove_section_from_relation(relation_id: str, section_id: str, req: Request):
        data = await req.app.state.relation_controller.remove_section(relation_id, section_id)
        return success_response(data, message="Section unlinked from relation successfully")

    return router
