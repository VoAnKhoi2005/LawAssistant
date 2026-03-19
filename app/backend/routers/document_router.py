from fastapi import APIRouter, Request, Query
from controllers.document_controller import DocumentController
from dto.document_dto import CreateDocumentRequest, UpdateDocumentRequest


def create_document_router_with_state() -> APIRouter:
    router = APIRouter(prefix="/api/documents", tags=["documents"])
    
    @router.get("/")
    async def get_all_documents(
        req: Request, 
        skip: int = Query(0, ge=0), 
        limit: int = Query(100, ge=1, le=1000)
    ):
        return await req.app.state.document_controller.get_all(skip, limit)
    
    @router.get("/{document_id}")
    async def get_document(document_id: str, req: Request):
        return await req.app.state.document_controller.get_by_id(document_id)
    
    @router.get("/by-so-hieu/{so_hieu}")
    async def get_document_by_so_hieu(so_hieu: str, req: Request):
        return await req.app.state.document_controller.get_by_so_hieu(so_hieu)
    
    @router.post("/")
    async def create_document(request: CreateDocumentRequest, req: Request):
        return await req.app.state.document_controller.create(request)
    
    @router.put("/{document_id}")
    async def update_document(document_id: str, request: UpdateDocumentRequest, req: Request):
        return await req.app.state.document_controller.update(document_id, request)
    
    @router.delete("/{document_id}")
    async def delete_document(document_id: str, req: Request):
        return await req.app.state.document_controller.delete(document_id)
    
    return router
