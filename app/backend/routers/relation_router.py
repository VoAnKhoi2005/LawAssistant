from fastapi import APIRouter, Request, Query
from controllers.relation_controller import RelationController
from dto.relation_dto import CreateRelationRequest, UpdateRelationRequest


def create_relation_router_with_state() -> APIRouter:
    router = APIRouter(prefix="/api/relations", tags=["relations"])
    
    @router.get("/")
    async def get_all_relations(
        req: Request, 
        skip: int = Query(0, ge=0), 
        limit: int = Query(100, ge=1, le=1000)
    ):
        return await req.app.state.relation_controller.get_all(skip, limit)
    
    @router.get("/by-name/{relation_name}")
    async def get_relations_by_name(
        relation_name: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
    ):
        return await req.app.state.relation_controller.get_by_name(relation_name, skip, limit)
    
    @router.get("/{relation_id}")
    async def get_relation(relation_id: str, req: Request):
        return await req.app.state.relation_controller.get_by_id(relation_id)
    
    @router.post("/")
    async def create_relation(request: CreateRelationRequest, req: Request):
        return await req.app.state.relation_controller.create(request)
    
    @router.put("/{relation_id}")
    async def update_relation(relation_id: str, request: UpdateRelationRequest, req: Request):
        return await req.app.state.relation_controller.update(relation_id, request)
    
    @router.delete("/{relation_id}")
    async def delete_relation(relation_id: str, req: Request):
        return await req.app.state.relation_controller.delete(relation_id)
    
    return router
