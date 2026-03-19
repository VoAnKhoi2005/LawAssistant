from fastapi import APIRouter, Request, Query
from controllers.concept_controller import ConceptController
from dto.concept_dto import CreateConceptRequest, UpdateConceptRequest


def create_concept_router_with_state() -> APIRouter:
    router = APIRouter(prefix="/api/concepts", tags=["concepts"])
    
    @router.get("/")
    async def get_all_concepts(
        req: Request, 
        skip: int = Query(0, ge=0), 
        limit: int = Query(100, ge=1, le=1000)
    ):
        return await req.app.state.concept_controller.get_all(skip, limit)
    
    @router.get("/search")
    async def search_concepts(
        name: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
    ):
        return await req.app.state.concept_controller.search_by_name(name, skip, limit)
    
    @router.get("/{concept_id}")
    async def get_concept(concept_id: str, req: Request):
        return await req.app.state.concept_controller.get_by_id(concept_id)
    
    @router.post("/")
    async def create_concept(request: CreateConceptRequest, req: Request):
        return await req.app.state.concept_controller.create(request)
    
    @router.put("/{concept_id}")
    async def update_concept(concept_id: str, request: UpdateConceptRequest, req: Request):
        return await req.app.state.concept_controller.update(concept_id, request)
    
    @router.delete("/{concept_id}")
    async def delete_concept(concept_id: str, req: Request):
        return await req.app.state.concept_controller.delete(concept_id)
    
    return router
