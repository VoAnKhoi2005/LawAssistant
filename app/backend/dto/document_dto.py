from pydantic import BaseModel, Field
from typing import Optional, List
from models.common import ObjectIdModel, DateModel, FileRef


class CreateDocumentRequest(BaseModel):
    so_hieu: str = Field(..., description="Document identifier (e.g., 01/2013/QH13)")
    title: str = Field(..., description="Document title")
    effective_date: str = Field(..., description="Effective date (YYYY-MM-DD)")
    file_ids: List[str] = Field(..., description="List of uploaded file IDs")


class UploadDocumentRequest(BaseModel):
    so_hieu: str = Field(..., description="Document identifier (e.g., 01/2013/QH13)")
    title: str = Field(..., description="Document title")
    effective_date: str = Field(..., description="Effective date (YYYY-MM-DD)")
    order: int = Field(default=1, description="Processing order priority")


class DocumentCreateResponse(BaseModel):
    document_id: str
    task_id: str
    status: str
    message: str
    file_refs: List[dict]


class TaskStatusResponse(BaseModel):
    task_id: str
    state: str
    progress: int = 0
    step: str = ""
    document_id: str = ""
    error: str = ""
    result: dict = {}


class UpdateDocumentRequest(BaseModel):
    effective_date: Optional[DateModel] = None
    is_active: Optional[bool] = None
    so_hieu: Optional[str] = None
    source_files: Optional[List[str]] = None
    title: Optional[str] = None


class DocumentResponse(BaseModel):
    id: ObjectIdModel = Field(..., alias="_id")
    effective_date: str
    is_active: bool
    so_hieu: str
    title: str
    files: List[FileRef]
    source_files: List[str]
    status: Optional[str] = None
    task_id: Optional[str] = None
    order: Optional[int] = None
    error: Optional[str] = None
    
    model_config = {
        "populate_by_name": True
    }
