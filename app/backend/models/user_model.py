from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    username: str
    email: EmailStr
    password: str

    model_config = {
        "populate_by_name": True
    }