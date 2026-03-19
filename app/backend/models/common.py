from datetime import datetime
from pydantic import BaseModel, Field

class ObjectIdModel(BaseModel):
    oid: str = Field(..., alias="$oid")
    model_config = {
        "populate_by_name": True
    }

class DateModel(BaseModel):
    date: datetime = Field(..., alias="$date")
    model_config = {
        "populate_by_name": True
    }

class DocumentRef(BaseModel):
    section_id: str
    so_hieu: str