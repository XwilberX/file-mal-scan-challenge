from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from core.config import settings

# Crear el engine async
engine = create_async_engine(
    settings.DATABASE_URI,
    echo=settings.DB_ECHO,
    future=True,
    poolclass=NullPool,
)

# Crear el async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia para obtener una sesión de base de datos."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
