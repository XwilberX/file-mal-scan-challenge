from datetime import UTC, datetime, timedelta

from sqlmodel import Field

from core.models import BaseModel, get_utc_now


class Token(BaseModel, table=True):
    """Modelo para tokens de autenticación."""

    access_token: str = Field(index=True)
    token_type: str = Field(default="bearer")
    user_id: int = Field(foreign_key="user.pkid", index=True)
    expires_at: datetime = Field(
        default_factory=lambda: get_utc_now() + timedelta(days=1)
    )
    is_valid: bool = Field(default=True)

    class Config:
        """Configuración del modelo."""

        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_at": "2024-03-21T12:00:00Z",
            }
        }
