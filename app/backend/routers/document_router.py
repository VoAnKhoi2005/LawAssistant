from fastapi import APIRouter, Depends, Request, Query

from core.security import get_current_user
from dto.document_dto import CreateDocumentRequest, UpdateDocumentRequest
from utils.response import success_response


def create_document_router_with_state() -> APIRouter:
    router = APIRouter(
        prefix="/api/documents",
        tags=["documents"],
        dependencies=[Depends(get_current_user)],
    )

    @router.get("/")
    async def get_all_documents(
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        data = await req.app.state.document_controller.get_all(skip, limit)
        return success_response(data, message="Documents retrieved successfully")

    @router.get("/{document_id}")
    async def get_document(document_id: str, req: Request):
        data = await req.app.state.document_controller.get_by_id(document_id)
        return success_response(data, message="Document retrieved successfully")

    @router.get("/by-so-hieu/{so_hieu}")
    async def get_document_by_so_hieu(so_hieu: str, req: Request):
        data = await req.app.state.document_controller.get_by_so_hieu(so_hieu)
        return success_response(data, message="Document retrieved successfully")

    @router.post("/")
    async def create_document(request: CreateDocumentRequest, req: Request):
        data = await req.app.state.document_controller.create(request)
        return success_response(data, message="Document created successfully")

    @router.put("/{document_id}")
    async def update_document(
        document_id: str, request: UpdateDocumentRequest, req: Request
    ):
        data = await req.app.state.document_controller.update(document_id, request)
        return success_response(data, message="Document updated successfully")

    @router.delete("/{document_id}")
    async def delete_document(document_id: str, req: Request):
        data = await req.app.state.document_controller.delete(document_id)
        return success_response(data, message="Document deleted successfully")

    return router
