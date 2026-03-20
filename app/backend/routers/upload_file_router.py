from fastapi import APIRouter, Depends, Request, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List
import io

from core.security import get_current_user
from dto.upload_file_dto import UpdateFileStatusRequest, UploadFileResponse, FileListResponse
from utils.api_response_helper import success_response


def create_upload_file_router_with_state() -> APIRouter:
    router = APIRouter(
        prefix="/api/upload-files",
        tags=["upload-files"],
        dependencies=[Depends(get_current_user)],
    )

    # @router.get("/", response_model=FileListResponse)
    # async def get_all_files(
    #     req: Request,
    #     skip: int = Query(0, ge=0),
    #     limit: int = Query(100, ge=1, le=1000),
    # ):
    #     files = await req.app.state.upload_file_controller.get_all(skip, limit)
    #     return success_response(files, message="Files retrieved successfully")

    @router.get("/{file_id}", response_model=UploadFileResponse)
    async def get_file(file_id: str, req: Request):
        file_data = await req.app.state.upload_file_controller.get_by_id(file_id)
        return success_response(file_data, message="File retrieved successfully")

    @router.get("/user/{user_id}", response_model=FileListResponse)
    async def get_files_by_user(
        user_id: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        files = await req.app.state.upload_file_controller.get_by_user_id(user_id, skip, limit)
        return success_response(files, message="User files retrieved successfully")

    @router.get("/status/{status}", response_model=FileListResponse)
    async def get_files_by_status(
        status: str,
        req: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        files = await req.app.state.upload_file_controller.get_by_status(status, skip, limit)
        return success_response(files, message=f"Files with status '{status}' retrieved successfully")

    @router.post("/upload", response_model=UploadFileResponse)
    async def upload_file(
        req: Request,
        file: UploadFile = File(...),
        user_id: str = Form(...)
    ):
        file_data = await req.app.state.upload_file_controller.upload_file(file, user_id)
        return success_response(file_data, message="File uploaded successfully")

    @router.post("/upload-multiple")
    async def upload_multiple_files(
        req: Request,
        files: List[UploadFile] = File(...),
        user_id: str = Form(...)
    ):
        result = await req.app.state.upload_file_controller.upload_multiple_files(files, user_id)
        return success_response(result, message="Files upload completed")

    @router.put("/{file_id}/status", response_model=UploadFileResponse)
    async def update_file_status(
        file_id: str,
        request: UpdateFileStatusRequest,
        req: Request
    ):
        file_data = await req.app.state.upload_file_controller.update_status(file_id, request)
        return success_response(file_data, message="File status updated successfully")

    @router.get("/{file_id}/download")
    async def download_file(file_id: str, req: Request):
        content, filename, content_type = await req.app.state.upload_file_controller.download(file_id)
        
        return StreamingResponse(
            io.BytesIO(content),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    @router.delete("/{file_id}")
    async def delete_file(file_id: str, req: Request):
        result = await req.app.state.upload_file_controller.delete(file_id)
        return success_response(result, message="File deleted successfully")

    return router