from typing import Optional, List
from bson import ObjectId

from pydantic import BaseModel, Field, field_validator

from models.common import DocumentRef


class Concept(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    description: Optional[str] = None
    documents: List[DocumentRef] = Field(default_factory=list)
    name: str
    synonym: List[str] = Field(default_factory=list)

    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    model_config = {
        "populate_by_name": True
    }
