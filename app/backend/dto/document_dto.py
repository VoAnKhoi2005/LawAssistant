from pydantic import BaseModel, Field
from typing import Optional, List
from models.common import ObjectIdModel, DateModel


class CreateDocumentRequest(BaseModel):
    effective_date: DateModel
    is_active: bool
    so_hieu: str
    source_files: List[str]
    title: str


class UploadDocumentRequest(BaseModel):
    so_hieu: str = Field(..., description="Document identifier (e.g., 01/2013/QH13)")
    title: str = Field(..., description="Document title")
    effective_date: str = Field(..., description="Effective date (YYYY-MM-DD)")
    order: int = Field(default=1, description="Processing order priority")


class DocumentUploadResponse(BaseModel):
    document_id: str
    task_id: str
    status: str
    message: str
    uploaded_files: List[str]


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
    effective_date: DateModel
    is_active: bool
    so_hieu: str
    source_files: List[str]
    title: str
    
    model_config = {
        "populate_by_name": True
    }
