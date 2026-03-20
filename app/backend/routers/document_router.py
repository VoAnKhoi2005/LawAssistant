from fastapi import APIRouter, Depends, Request, Query
from typing import List

from core.security import get_current_user
from dto.document_dto import CreateDocumentRequest, UpdateDocumentRequest
from utils.api_response_helper import success_response


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
        current_user: dict = Depends(get_current_user),
    ):
        """Get all documents for the current user"""
        user_id = current_user.get("id")
        data = await req.app.state.document_controller.get_all(skip, limit, user_id)
        return success_response(data, message="Documents retrieved successfully")

    @router.get("/{document_id}")
    async def get_document(
        document_id: str, 
        req: Request,
        current_user: dict = Depends(get_current_user),
    ):
        """Get document by ID with authorization check"""
        user_id = current_user.get("id")
        data = await req.app.state.document_controller.get_by_id(document_id, user_id)
        return success_response(data, message="Document retrieved successfully")

    @router.get("/by-so-hieu/{so_hieu}")
    async def get_document_by_so_hieu(
        so_hieu: str, 
        req: Request,
        current_user: dict = Depends(get_current_user),
    ):
        """Get document by so_hieu with authorization check"""
        user_id = current_user.get("id")
        data = await req.app.state.document_controller.get_by_so_hieu(so_hieu, user_id)
        return success_response(data, message="Document retrieved successfully")

    @router.post("/")
    async def create_document(
        request: CreateDocumentRequest, 
        req: Request,
        current_user: dict = Depends(get_current_user),
    ):
        """Create document with user_id from JWT token"""
        user_id = current_user.get("id")
        data = await req.app.state.document_controller.create(request, user_id)
        return success_response(data, message="Document created successfully")

    @router.put("/{document_id}")
    async def update_document(
        document_id: str, 
        request: UpdateDocumentRequest, 
        req: Request,
        current_user: dict = Depends(get_current_user),
    ):
        """Update document with authorization check"""
        user_id = current_user.get("id")
        data = await req.app.state.document_controller.update(document_id, request, user_id)
        return success_response(data, message="Document updated successfully")

    @router.delete("/{document_id}")
    async def delete_document(
        document_id: str, 
        req: Request,
        current_user: dict = Depends(get_current_user),
    ):
        """Delete document with authorization check"""
        user_id = current_user.get("id")
        data = await req.app.state.document_controller.delete(document_id, user_id)
        return success_response(data, message="Document deleted successfully")

    return router
