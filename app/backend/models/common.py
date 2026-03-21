from datetime import datetime
from typing import Optional, Any
from bson import ObjectId

from pydantic import BaseModel, Field, field_serializer, field_validator


def serialize_object_id(obj_id: Any) -> Optional[str]:
    """Convert ObjectId to string"""
    if obj_id is None:
        return None
    if isinstance(obj_id, ObjectId):
        return str(obj_id)
    return str(obj_id)


class ObjectIdModel(BaseModel):
    oid: str = Field(..., alias="$oid")
    model_config = {
        "populate_by_name": True
    }

class DateModel(BaseModel):
    date: datetime = Field(..., alias="$date")
    model_config = {
        "populate_by_name": True
    }

class DocumentRef(BaseModel):
    section_id: str
    so_hieu: str

class FileRef(BaseModel):
    file_id: str
    filename: Optional[str] = None