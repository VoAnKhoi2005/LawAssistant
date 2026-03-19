from fastapi import APIRouter, Depends, Request, Query

from controllers.triplet_controller import TripletController, AddSectionToTripletRequest
from core.security import get_current_user
from dto.triplet_dto import CreateTripletRequest, UpdateTripletRequest
from utils.response import success_response


def create_triplet_router_with_state() -> APIRouter:
    router = APIRouter(
        prefix="/api/triplets",
        tags=["triplets"],
        dependencies=[Depends(get_current_user)],
    )

    @router.get("/")
    async def get_all_triplets(
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.triplet_controller.get_all(skip, limit)
        return success_response(data, message="Triplets retrieved successfully")

    @router.get("/by-subject/{subject_id}")
    async def get_triplets_by_subject(
        subject_id: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.triplet_controller.get_by_subject(subject_id, skip, limit)
        return success_response(data, message="Triplets retrieved successfully")

    @router.get("/by-object/{object_id}")
    async def get_triplets_by_object(
        object_id: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.triplet_controller.get_by_object(object_id, skip, limit)
        return success_response(data, message="Triplets retrieved successfully")

    @router.get("/{triplet_id}")
    async def get_triplet(triplet_id: str, req: Request):
        data = await req.app.state.triplet_controller.get_by_id(triplet_id)
        return success_response(data, message="Triplet retrieved successfully")

    @router.post("/")
    async def create_triplet(request: CreateTripletRequest, req: Request):
        data = await req.app.state.triplet_controller.create(request)
        return success_response(data, message="Triplet created successfully")

    @router.put("/{triplet_id}")
    async def update_triplet(triplet_id: str, request: UpdateTripletRequest, req: Request):
        data = await req.app.state.triplet_controller.update(triplet_id, request)
        return success_response(data, message="Triplet updated successfully")

    @router.delete("/{triplet_id}")
    async def delete_triplet(triplet_id: str, req: Request):
        data = await req.app.state.triplet_controller.delete(triplet_id)
        return success_response(data, message="Triplet deleted successfully")

    # Section association endpoints
    @router.post("/{triplet_id}/sections")
    async def add_section_to_triplet(
        triplet_id: str, request: AddSectionToTripletRequest, req: Request
    ):
        data = await req.app.state.triplet_controller.add_section(triplet_id, request)
        return success_response(data, message="Section linked to triplet successfully")

    @router.delete("/{triplet_id}/sections/{section_id}")
    async def remove_section_from_triplet(triplet_id: str, section_id: str, req: Request):
        data = await req.app.state.triplet_controller.remove_section(triplet_id, section_id)
        return success_response(data, message="Section unlinked from triplet successfully")

    return router
