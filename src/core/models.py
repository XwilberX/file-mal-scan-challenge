from datetime import UTC, datetime
from typing import Optional

from sqlmodel import Field, SQLModel


def get_utc_now() -> datetime:
    """Retorna la fecha actual en UTC sin zona horaria."""
    return datetime.now(UTC).replace(tzinfo=None)


class BaseModel(SQLModel):
    """Modelo base del cual heredarán todos los demás modelos."""

    pkid: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)
    updated_at: datetime = Field(
        default_factory=get_utc_now,
        sa_column_kwargs={"onupdate": get_utc_now},
        nullable=False,
    )

    class Config:
        """Configuración del modelo."""

        arbitrary_types_allowed = True
