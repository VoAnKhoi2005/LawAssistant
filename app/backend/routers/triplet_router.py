from fastapi import APIRouter, Request, Query
from controllers.triplet_controller import TripletController
from dto.triplet_dto import CreateTripletRequest, UpdateTripletRequest


def create_triplet_router_with_state() -> APIRouter:
    router = APIRouter(prefix="/api/triplets", tags=["triplets"])
    
    @router.get("/")
    async def get_all_triplets(
        req: Request, 
        skip: int = Query(0, ge=0), 
        limit: int = Query(100, ge=1, le=1000)
    ):
        return await req.app.state.triplet_controller.get_all(skip, limit)
    
    @router.get("/by-subject/{subject_id}")
    async def get_triplets_by_subject(
        subject_id: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
    ):
        return await req.app.state.triplet_controller.get_by_subject(subject_id, skip, limit)
    
    @router.get("/by-object/{object_id}")
    async def get_triplets_by_object(
        object_id: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
    ):
        return await req.app.state.triplet_controller.get_by_object(object_id, skip, limit)
    
    @router.get("/{triplet_id}")
    async def get_triplet(triplet_id: str, req: Request):
        return await req.app.state.triplet_controller.get_by_id(triplet_id)
    
    @router.post("/")
    async def create_triplet(request: CreateTripletRequest, req: Request):
        return await req.app.state.triplet_controller.create(request)
    
    @router.put("/{triplet_id}")
    async def update_triplet(triplet_id: str, request: UpdateTripletRequest, req: Request):
        return await req.app.state.triplet_controller.update(triplet_id, request)
    
    @router.delete("/{triplet_id}")
    async def delete_triplet(triplet_id: str, req: Request):
        return await req.app.state.triplet_controller.delete(triplet_id)
    
    return router
