from typing import Optional, List

from pydantic import BaseModel, Field

from models.common import ObjectIdModel, DocumentRef


class Concept(BaseModel):
    id: ObjectIdModel = Field(..., alias="_id")
    description: Optional[None] = None
    documents: List[DocumentRef]
    name: str
    synonym: List[str]

    model_config = {
        "populate_by_name": True
    }