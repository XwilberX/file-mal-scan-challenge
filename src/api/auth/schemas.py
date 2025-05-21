from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    """Esquema para tokens de autenticación."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_at": "2024-03-21T12:00:00Z",
            }
        }
    )

    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class TokenPayload(BaseModel):
    """Schema para el payload del token JWT."""

    sub: Optional[str] = None
    exp: Optional[float] = None


class TokenData(BaseModel):
    """Schema para datos del token."""

    user_id: Optional[int] = None
