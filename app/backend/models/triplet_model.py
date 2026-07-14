from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator
from models.common import DocumentRef


class Triplet(BaseModel):
    id: Optional[str] = Field(None, alias="_id")

    documents: List[DocumentRef] = Field(default_factory=list)

    object_id: Optional[str] = None
    object_name: str

    relation_id: Optional[str] = None
    relation_name: str

    subject_id: Optional[str] = None
    subject_name: str

    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    model_config = {
        "populate_by_name": True
    }
