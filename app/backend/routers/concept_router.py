from fastapi import APIRouter, Depends, Request, Query

from controllers.concept_controller import AddSectionToConceptRequest
from core.security import get_current_user
from dto.concept_dto import CreateConceptRequest, UpdateConceptRequest
from utils.response import success_response


def create_concept_router_with_state() -> APIRouter:
    router = APIRouter(
        prefix="/api/concepts",
        tags=["concepts"],
        dependencies=[Depends(get_current_user)],
    )

    @router.get("/")
    async def get_all_concepts(
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.concept_controller.get_all(skip, limit)
        return success_response(data, message="Concepts retrieved successfully")

    @router.get("/search")
    async def search_concepts(
        name: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.concept_controller.search_by_name(name, skip, limit)
        return success_response(data, message="Concepts retrieved successfully")

    @router.get("/{concept_id}")
    async def get_concept(concept_id: str, req: Request):
        data = await req.app.state.concept_controller.get_by_id(concept_id)
        return success_response(data, message="Concept retrieved successfully")

    @router.post("/")
    async def create_concept(request: CreateConceptRequest, req: Request):
        data = await req.app.state.concept_controller.create(request)
        return success_response(data, message="Concept created successfully")

    @router.put("/{concept_id}")
    async def update_concept(concept_id: str, request: UpdateConceptRequest, req: Request):
        data = await req.app.state.concept_controller.update(concept_id, request)
        return success_response(data, message="Concept updated successfully")

    @router.delete("/{concept_id}")
    async def delete_concept(concept_id: str, req: Request):
        data = await req.app.state.concept_controller.delete(concept_id)
        return success_response(data, message="Concept deleted successfully")

    # Section association endpoints
    @router.post("/{concept_id}/sections")
    async def add_section_to_concept(
        concept_id: str, request: AddSectionToConceptRequest, req: Request
    ):
        data = await req.app.state.concept_controller.add_section(concept_id, request)
        return success_response(data, message="Section linked to concept successfully")

    @router.delete("/{concept_id}/sections/{section_id}")
    async def remove_section_from_concept(concept_id: str, section_id: str, req: Request):
        data = await req.app.state.concept_controller.remove_section(concept_id, section_id)
        return success_response(data, message="Section unlinked from concept successfully")

    return router
