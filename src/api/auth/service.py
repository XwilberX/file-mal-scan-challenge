from datetime import UTC, datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from sqlmodel.ext.asyncio.session import AsyncSession

from core.config import settings
from core.models import get_utc_now
from api.users.service import UserService
from .repository import TokenRepository
from .schemas import TokenPayload


class AuthService:
    """Servicio para la autenticación."""

    def __init__(self, session: AsyncSession):
        """Inicializa el servicio."""
        self.session = session
        self.user_service = UserService(session)
        self.token_repository = TokenRepository(session)

    async def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """Autentica un usuario."""
        return await self.user_service.authenticate(email, password)

    def create_access_token(self, user_id: int) -> tuple[str, datetime]:
        """Crea un token de acceso."""
        expire = get_utc_now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"exp": expire.timestamp(), "sub": str(user_id)}
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        return encoded_jwt, expire

    async def get_current_user(self, token: str) -> Optional[dict]:
        """Obtiene el usuario actual a partir del token."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            token_data = TokenPayload(**payload)
        except JWTError:
            return None

        if token_data.sub is None:
            return None

        user = await self.user_service.get_user(int(token_data.sub))
        if user is None:
            return None

        return user

    async def create_user_token(self, user_id: int) -> Optional[dict]:
        """Crea un token para un usuario."""
        token, expires_at = self.create_access_token(user_id)
        token_data = {
            "access_token": token,
            "user_id": user_id,
            "expires_at": expires_at,
        }
        return await self.token_repository.create(obj_in=token_data)

    async def revoke_token(self, token_id: int) -> bool:
        """Revoca un token."""
        token = await self.token_repository.get(token_id)
        if not token:
            return False

        return await self.token_repository.update(
            db_obj=token, obj_in={"is_valid": False}
        )
