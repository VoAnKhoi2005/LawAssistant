from pydantic import BaseModel, Field
from typing import Optional, List
from models.common import ObjectIdModel, DocumentRef


class CreateConceptRequest(BaseModel):
    description: Optional[str] = None
    documents: List[DocumentRef]
    name: str
    synonym: List[str]


class UpdateConceptRequest(BaseModel):
    description: Optional[str] = None
    documents: Optional[List[DocumentRef]] = None
    name: Optional[str] = None
    synonym: Optional[List[str]] = None


class ConceptResponse(BaseModel):
    id: ObjectIdModel = Field(..., alias="_id")
    description: Optional[str] = None
    documents: List[DocumentRef]
    name: str
    synonym: List[str]
    
    model_config = {
        "populate_by_name": True
    }
