from pydantic import BaseModel, Field
from typing import Optional


class CreateLegalSectionRequest(BaseModel):
    content: Optional[str] = None
    document_title: str
    effective_date: str
    full_path: str
    section_id: str = Field(..., alias="id")
    parent_id: Optional[str] = None
    so_hieu: str
    source_file: str
    title: str
    type: str
    is_amendment: Optional[bool] = None
    is_phu_luc: Optional[bool] = None


class UpdateLegalSectionRequest(BaseModel):
    content: Optional[str] = None
    document_title: Optional[str] = None
    effective_date: Optional[str] = None
    full_path: Optional[str] = None
    parent_id: Optional[str] = None
    so_hieu: Optional[str] = None
    source_file: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    is_amendment: Optional[bool] = None
    is_phu_luc: Optional[bool] = None


class LegalSectionResponse(BaseModel):
    id: str = Field(..., alias="_id")
    content: Optional[str] = None
    document_title: str
    effective_date: str
    full_path: str
    section_id: str = Field(..., alias="id")
    parent_id: Optional[str] = None
    so_hieu: str
    source_file: str
    title: str
    type: str
    is_amendment: Optional[bool] = None
    is_phu_luc: Optional[bool] = None
    
    model_config = {
        "populate_by_name": True
    }
