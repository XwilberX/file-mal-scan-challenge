from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession
from passlib.context import CryptContext

from .repository import UserRepository
from .schemas import UserCreate, UserUpdate


class UserService:
    """Servicio para la lógica de negocio de usuarios."""

    def __init__(self, session: AsyncSession):
        """Inicializa el servicio."""
        self.repository = UserRepository(session)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica si la contraseña es correcta."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Genera el hash de una contraseña."""
        return self.pwd_context.hash(password)

    async def create_user(self, user_in: UserCreate) -> Optional[dict]:
        """Crea un nuevo usuario."""
        # Verificar si el usuario ya existe
        if await self.repository.get_by_email(user_in.email):
            return None

        # Crear el usuario
        user_data = user_in.model_dump()
        hashed_password = self.get_password_hash(user_data.pop("password"))
        user_data["hashed_password"] = hashed_password

        return await self.repository.create(obj_in=user_data)

    async def update_user(self, user_id: int, user_in: UserUpdate) -> Optional[dict]:
        """Actualiza un usuario existente."""
        user = await self.repository.get(user_id)
        if not user:
            return None

        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = self.get_password_hash(
                update_data.pop("password")
            )

        return await self.repository.update(db_obj=user, obj_in=update_data)

    async def authenticate(self, email: str, password: str) -> Optional[dict]:
        """Autentica un usuario."""
        user = await self.repository.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def get_user(self, user_id: int) -> Optional[dict]:
        """Obtiene un usuario por su ID."""
        return await self.repository.get(user_id)

    async def get_by_email(self, email: str) -> Optional[dict]:
        """Obtiene un usuario por su email."""
        return await self.repository.get_by_email(email)

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[dict]:
        """Obtiene una lista de usuarios."""
        return await self.repository.list(skip=skip, limit=limit)

    async def delete_user(self, user_id: int) -> bool:
        """Elimina un usuario."""
        return await self.repository.delete(pkid=user_id)
