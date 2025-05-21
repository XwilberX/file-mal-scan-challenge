from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.repository import BaseRepository
from .models import FileScan


class ScanRepository(BaseRepository[FileScan]):
    """Repositorio para operaciones con escaneos."""

    def __init__(self, session: AsyncSession):
        """Inicializa el repositorio."""
        super().__init__(model=FileScan, session=session)

    async def get_by_hash(self, hash_value: str) -> Optional[FileScan]:
        """Busca un escaneo por cualquiera de sus hashes."""
        statement = select(self.model).where(
            (self.model.md5_hash == hash_value)
            | (self.model.sha1_hash == hash_value)
            | (self.model.sha256_hash == hash_value)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
