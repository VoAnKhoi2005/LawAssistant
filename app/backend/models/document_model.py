from typing import List, Optional
from bson import ObjectId
from pydantic import BaseModel, Field, field_validator
from models.common import ObjectIdModel, DateModel, FileRef


class Document(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    effective_date: DateModel
    is_active: bool
    so_hieu: str
    source_files: List[FileRef]
    title: str
    files: Optional[List[FileRef]] = None
    status: Optional[str] = None
    task_id: Optional[str] = None

    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    model_config = {
        "populate_by_name": True
    }