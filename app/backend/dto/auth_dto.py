from pydantic import BaseModel
from typing import Optional
from dto.user_dto import UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenPairResponse
