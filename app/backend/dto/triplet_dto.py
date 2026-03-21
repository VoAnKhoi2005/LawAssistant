from pydantic import BaseModel, Field
from typing import Optional, List
from models.common import ObjectIdModel, DocumentRef


class CreateTripletRequest(BaseModel):
    documents: List[DocumentRef]
    object_id: ObjectIdModel
    object_name: str
    relation_id: ObjectIdModel
    relation_name: str
    subject_id: ObjectIdModel
    subject_name: str


class UpdateTripletRequest(BaseModel):
    documents: Optional[List[DocumentRef]] = None
    object_id: Optional[ObjectIdModel] = None
    object_name: Optional[str] = None
    relation_id: Optional[ObjectIdModel] = None
    relation_name: Optional[str] = None
    subject_id: Optional[ObjectIdModel] = None
    subject_name: Optional[str] = None


class TripletResponse(BaseModel):
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
