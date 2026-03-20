from typing import List, Optional
from pydantic import BaseModel, Field
from models.common import ObjectIdModel, DateModel, FileRef


class Document(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    effective_date: DateModel
    is_active: bool
    so_hieu: str
    source_files: List[FileRef]
    title: str
    files: Optional[List[FileRef]] = None
    status: Optional[str] = None
    task_id: Optional[str] = None

    model_config = {
        "populate_by_name": True
    }