from pydantic import BaseModel
from typing import List, Optional
from models.common import ObjectIdModel, DocumentRef


class AddConceptToSectionRequest(BaseModel):
    section_id: str
    concept_id: str


class AddRelationToSectionRequest(BaseModel):
    section_id: str
    relation_id: str


class AddTripletToSectionRequest(BaseModel):
    section_id: str
    triplet_id: str


class SectionConceptResponse(BaseModel):
    section_id: str
    concept_id: str
    concept_name: str


class SectionRelationAssociationResponse(BaseModel):
    section_id: str
    relation_id: str
    relation_name: str


class SectionTripletResponse(BaseModel):
    section_id: str
    triplet_id: str
    subject_name: str
    relation_name: str
    object_name: str
