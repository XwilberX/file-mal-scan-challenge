from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.repository import BaseRepository
from .models import User


class UserRepository(BaseRepository[User]):
    """Repositorio para operaciones con usuarios."""

    def __init__(self, session: AsyncSession):
        """Inicializa el repositorio de usuarios."""
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por su email."""
        return await self.get_by_field("email", email)

    async def get_active_users(self, *, skip: int = 0, limit: int = 100) -> list[User]:
        """Lista usuarios activos con paginación."""
        query = select(self.model).where(self.model.is_active).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
