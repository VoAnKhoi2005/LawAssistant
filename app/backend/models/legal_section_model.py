from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator


class LegalSection(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
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

    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    model_config = {
        "populate_by_name": True
    }