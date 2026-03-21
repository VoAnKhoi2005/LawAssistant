from bson import ObjectId
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class UploadedFile(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str

    file_id: str
    filename: str
    storage_path: str
    content_type: Optional[str] = None
    size: Optional[int] = None

    status: str = "uploaded"  # uploaded | processing | done | failed
    error: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    model_config = {
        "populate_by_name": True
    }