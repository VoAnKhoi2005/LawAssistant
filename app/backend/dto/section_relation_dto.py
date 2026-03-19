from pydantic import BaseModel, Field
from typing import Optional, List
from models.common import ObjectIdModel
from models.section_relation_model import RefDetails


class CreateSectionRelationRequest(BaseModel):
    source: str
    target: str
    type: str
    amendment_types: Optional[List[str]] = None
    ref_details: Optional[RefDetails] = None


class UpdateSectionRelationRequest(BaseModel):
    source: Optional[str] = None
    target: Optional[str] = None
    type: Optional[str] = None
    amendment_types: Optional[List[str]] = None
    ref_details: Optional[RefDetails] = None


class SectionRelationResponse(BaseModel):
    id: ObjectIdModel = Field(..., alias="_id")
    source: str
    target: str
    type: str
    amendment_types: Optional[List[str]] = None
    ref_details: Optional[RefDetails] = None
    
    model_config = {
        "populate_by_name": True
    }
