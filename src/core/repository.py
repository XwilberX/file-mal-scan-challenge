from typing import Any, Generic, Optional, Type, TypeVar, List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Implementación base del patrón repository."""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """Inicializa el repositorio."""
        self.model = model
        self.session = session

    async def get(self, pkid: Any) -> Optional[ModelType]:
        """Obtiene un registro por su ID."""
        return await self.session.get(self.model, pkid)

    async def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """Obtiene un registro por un campo específico."""
        query = select(self.model).where(getattr(self.model, field) == value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Lista registros con paginación."""
        query = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict[str, Any]] = None,
    ) -> List[ModelType]:
        """Lista registros con paginación y filtros opcionales."""
        query = select(self.model)

        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, *, obj_in: dict[str, Any]) -> ModelType:
        """Crea un nuevo registro."""
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, *, db_obj: ModelType, obj_in: dict[str, Any]) -> ModelType:
        """Actualiza un registro existente."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, *, pkid: Any) -> bool:
        """Elimina un registro."""
        obj = await self.get(pkid)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()
            return True
        return False
