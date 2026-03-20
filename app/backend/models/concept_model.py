from typing import Optional, List

from pydantic import BaseModel, Field

from models.common import DocumentRef


class Concept(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    description: Optional[str] = None
    documents: List[DocumentRef] = []
    name: str
    synonym: List[str] = []

    model_config = {
        "populate_by_name": True
    }