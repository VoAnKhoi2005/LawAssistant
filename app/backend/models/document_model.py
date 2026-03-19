from typing import List
from pydantic import BaseModel, Field
from models.common import ObjectIdModel, DateModel


class Document(BaseModel):
    id: ObjectIdModel = Field(..., alias="_id")
    effective_date: DateModel
    is_active: bool
    so_hieu: str
    source_files: List[str]
    title: str

    model_config = {
        "populate_by_name": True
    }