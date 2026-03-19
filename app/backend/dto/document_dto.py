from pydantic import BaseModel, Field
from typing import Optional, List
from models.common import ObjectIdModel, DateModel


class CreateDocumentRequest(BaseModel):
    effective_date: DateModel
    is_active: bool
    so_hieu: str
    source_files: List[str]
    title: str


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
