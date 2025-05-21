from typing import Optional

from sqlmodel import Field

from core.models import BaseModel


class User(BaseModel, table=True):
    """Modelo de usuario."""

    email: str = Field(unique=True, index=True)
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    full_name: Optional[str] = Field(default=None)

    class Config:
        """Configuración del modelo."""

        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "is_superuser": False,
            }
        }
