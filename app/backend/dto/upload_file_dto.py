from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models.common import ObjectIdModel


class UploadFileRequest(BaseModel):
    user_id: str = Field(..., description="User ID who owns the file")


class UploadFileResponse(BaseModel):
    id: ObjectIdModel = Field(..., alias="_id")
    user_id: str
    filename: str
    storage_path: str
    content_type: Optional[str] = None
    size: Optional[int] = None
    status: str
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "populate_by_name": True
    }


class UploadMultipleFilesResponse(BaseModel):
    uploaded_files: List[UploadFileResponse]
    failed_files: Optional[List[dict]] = None
    message: Optional[str] = None


class UpdateFileStatusRequest(BaseModel):
    status: str = Field(..., description="New status: uploaded, processing, done, failed")
    error: Optional[str] = Field(None, description="Error message if status is failed")


class FileListResponse(BaseModel):
    files: List[UploadFileResponse]
    total: int
    skip: int
    limit: int