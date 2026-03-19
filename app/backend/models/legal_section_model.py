from typing import Optional

from pydantic import BaseModel, Field


class LegalSection(BaseModel):
    id: str = Field(..., alias="_id")
    content: Optional[str] = None
    document_title: str
    effective_date: str
    full_path: str
    section_id: str = Field(..., alias="id")
    parent_id: Optional[str] = None
    so_hieu: str
    source_file: str
    title: str
    type: str

    is_amendment: Optional[bool] = None
    is_phu_luc: Optional[bool] = None

    model_config = {
        "populate_by_name": True
    }