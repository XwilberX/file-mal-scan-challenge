from datetime import UTC, datetime
from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.repository import BaseRepository
from .models import Token


class TokenRepository(BaseRepository[Token]):
    """Repositorio para operaciones con tokens."""

    def __init__(self, session: AsyncSession):
        """Inicializa el repositorio de tokens."""
        super().__init__(Token, session)

    async def get_valid_token(self, token: str) -> Optional[Token]:
        """Obtiene un token válido."""
        query = select(self.model).where(
            self.model.access_token == token,
            self.model.is_valid == True,  # noqa: E712
            self.model.expires_at > datetime.now(UTC),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_tokens(self, user_id: int) -> list[Token]:
        """Obtiene todos los tokens de un usuario."""
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
