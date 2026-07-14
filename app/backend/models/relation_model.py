from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator, model_validator

from models.common import DocumentRef


class Relation(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    documents: List[DocumentRef] = Field(default_factory=list)
    description: Optional[str] = None
    synonym: List[str] = Field(default_factory=list)

    object_id: Optional[str] = None
    object_name: Optional[str] = None

    relation_id: Optional[str] = None
    name: str

    subject_id: Optional[str] = None
    subject_name: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def normalize_relation_name(cls, data):
        if isinstance(data, dict):
            normalized = dict(data)
            if "name" not in normalized and "relation_name" in normalized:
                normalized["name"] = normalized["relation_name"]
            return normalized
        return data

    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    @property
    def relation_name(self) -> str:
        return self.name

    model_config = {
        "populate_by_name": True
    }
