from typing import Optional
from bson import ObjectId

from pydantic import BaseModel, Field, EmailStr, field_validator


class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    username: str
    email: EmailStr
    password: str

    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    model_config = {
        "populate_by_name": True
    }