from typing import Annotated

from fastapi import APIRouter, Depends, status, Form, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from core.database import get_session
from core.exceptions import ValidationAPIError
from core.schemas import Response, create_response
from .schemas import Token
from .service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


async def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuthService:
    """Dependencia para obtener el servicio de autenticación."""
    return AuthService(session)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Dependencia para obtener el usuario actual."""
    if not credentials:
        raise ValidationAPIError(
            message="Authentication required",
            errors=["Token not provided"],
        )

    user = await service.get_current_user(credentials.credentials)
    if not user:
        raise ValidationAPIError(
            message="Could not validate credentials",
            errors=["Invalid or expired token"],
        )
    return user


@router.post("/token", response_model=Response[Token])
async def login_for_access_token(
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Endpoint para obtener un token de acceso."""
    user = await service.authenticate_user(email, password)
    if not user:
        raise ValidationAPIError(
            message="Authentication failed", errors=["Incorrect email or password"]
        )
    token = await service.create_user_token(user.pkid)
    return create_response(data=token, message="Authentication successful")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Endpoint para cerrar sesión (revocar token)."""
    if not credentials:
        return create_response(
            data=None, code=status.HTTP_204_NO_CONTENT, message="No token provided"
        )

    current_token = await service.token_repository.get_valid_token(
        credentials.credentials
    )
    if current_token:
        await service.revoke_token(current_token.pkid)
    return create_response(
        data=None, code=status.HTTP_204_NO_CONTENT, message="Logged out successfully"
    )
