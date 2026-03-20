import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, Request, Query, UploadFile, File, Form, HTTPException
from typing import List

from core.celery_app import celery_app
from core.security import get_current_user
from dto.document_dto import (
    CreateDocumentRequest, 
    UpdateDocumentRequest,
    DocumentUploadResponse,
    TaskStatusResponse
)
from utils.api_response_helper import success_response
from worker.tasks.document_processing_tasks import process_document


def create_document_router_with_state() -> APIRouter:
    router = APIRouter(
        prefix="/api/documents",
        tags=["documents"],
        dependencies=[Depends(get_current_user)],
    )

    # Ensure uploads directory exists
    UPLOADS_DIR = Path("uploads")
    UPLOADS_DIR.mkdir(exist_ok=True)

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

    @router.post("/upload")
    async def upload_document(
        so_hieu: str = Form(...),
        title: str = Form(...),
        effective_date: str = Form(...),
        order: int = Form(default=1),
        files: List[UploadFile] = File(...)
    ):
        """
        Upload documents and queue for processing
        Accepts PDF and DOCX files with metadata
        """
        # Validate file types
        allowed_extensions = {".pdf", ".docx"}
        uploaded_files = []
        
        for file in files:
            if not file.filename:
                raise HTTPException(status_code=400, detail="File name is required")
                
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} has unsupported format. Only PDF and DOCX files are allowed."
                )
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        doc_upload_dir = UPLOADS_DIR / document_id
        doc_upload_dir.mkdir(exist_ok=True)
        
        # Save uploaded files
        file_paths = []
        for file in files:
            file_path = doc_upload_dir / file.filename
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            file_paths.append(str(file_path))
            uploaded_files.append(file.filename)
        
        # Prepare metadata for task
        metadata = {
            "so_hieu": so_hieu,
            "title": title,
            "effective_date": effective_date,
            "order": order,
            "file_count": len(files)
        }
        
        # Queue processing task
        task = process_document.delay(
            document_id=document_id,
            file_path=str(doc_upload_dir),  # Pass directory path containing all files
            metadata=metadata
        )
        
        response = DocumentUploadResponse(
            document_id=document_id,
            task_id=task.id,
            status="queued",
            message="Document uploaded and queued for processing",
            uploaded_files=uploaded_files
        )
        
        return success_response(response.dict(), message="Document upload successful")

    @router.get("/task/{task_id}/status")
    async def get_task_status(task_id: str):
        """
        Get the status of a document processing task
        """
        try:
            task_result = celery_app.AsyncResult(task_id)
            
            if task_result.state == "PENDING":
                response = TaskStatusResponse(
                    task_id=task_id,
                    state="PENDING",
                    step="Task is waiting in queue"
                )
            elif task_result.state == "PROCESSING":
                info = task_result.info or {}
                response = TaskStatusResponse(
                    task_id=task_id,
                    state="PROCESSING",
                    progress=info.get("progress", 0),
                    step=info.get("step", "Processing..."),
                    document_id=info.get("document_id", "")
                )
            elif task_result.state == "SUCCESS":
                result = task_result.result or {}
                response = TaskStatusResponse(
                    task_id=task_id,
                    state="SUCCESS",
                    progress=100,
                    step="Processing completed",
                    document_id=result.get("document_id", ""),
                    result=result
                )
            elif task_result.state == "FAILURE":
                info = task_result.info or {}
                response = TaskStatusResponse(
                    task_id=task_id,
                    state="FAILURE",
                    step=info.get("step", "Processing failed"),
                    document_id=info.get("document_id", ""),
                    error=info.get("error", str(task_result.info))
                )
            else:
                response = TaskStatusResponse(
                    task_id=task_id,
                    state=task_result.state,
                    step=f"Task state: {task_result.state}"
                )
            
            return success_response(response.dict(), message="Task status retrieved")
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving task status: {str(e)}")

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
