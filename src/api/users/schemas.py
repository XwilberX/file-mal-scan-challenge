from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Schema base para usuarios."""

    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema para crear usuarios."""

    password: str


class UserUpdate(UserBase):
    """Schema para actualizar usuarios."""

    password: Optional[str] = None


class UserInDB(UserBase):
    """Schema para usuario en la base de datos."""

    pkid: int
    hashed_password: str

    class Config:
        """Configuración del schema."""

        from_attributes = True


class UserResponse(UserBase):
    """Schema para respuesta de usuario."""

    pkid: int

    class Config:
        """Configuración del schema."""

        from_attributes = True
