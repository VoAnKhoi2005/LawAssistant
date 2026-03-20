from typing import Optional, List
from pydantic import BaseModel, Field


class RefDetails(BaseModel):
    chuong: Optional[str] = None
    diem: Optional[str] = None
    dieu: str
    khoan: Optional[str] = None
    muc: Optional[str] = None
    phan: Optional[str] = None
    phu_luc: Optional[str] = None
    so_hieu: str
    tieu_muc: Optional[str] = None

class SectionRelation(BaseModel):
    id: Optional[str] = Field(None, alias="_id")

    source: str
    target: str
    type: str

    amendment_types: Optional[List[str]] = None
    ref_details: Optional[RefDetails] = None

    model_config = {
        "populate_by_name": True
    }