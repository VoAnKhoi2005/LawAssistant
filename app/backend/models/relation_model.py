from typing import List, Optional

from pydantic import BaseModel, Field

from models.common import DocumentRef


class Relation(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    documents: List[DocumentRef] = []

    object_id: Optional[str] = None
    object_name: str

    relation_id: Optional[str] = None
    relation_name: str

    subject_id: Optional[str] = None
    subject_name: str

    model_config = {
        "populate_by_name": True
    }