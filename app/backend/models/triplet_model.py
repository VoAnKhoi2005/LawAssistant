from typing import List
from pydantic import BaseModel, Field
from models.common import ObjectIdModel, DocumentRef


class Triplet(BaseModel):
    id: ObjectIdModel = Field(..., alias="_id")

    documents: List[DocumentRef]

    object_id: ObjectIdModel
    object_name: str

    relation_id: ObjectIdModel
    relation_name: str

    subject_id: ObjectIdModel
    subject_name: str

    model_config = {
        "populate_by_name": True
    }