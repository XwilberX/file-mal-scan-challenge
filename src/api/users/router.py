from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from api.auth.router import get_current_user
from core.database import get_session
from core.exceptions import NotFoundError, ValidationAPIError
from core.schemas import Response, create_response
from .schemas import UserCreate, UserResponse, UserUpdate
from .service import UserService

router = APIRouter(prefix="/users", tags=["users"])


async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    """Dependencia para obtener el servicio de usuarios."""
    return UserService(session)


@router.post(
    "/", response_model=Response[UserResponse], status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_in: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
):
    """Crea un nuevo usuario."""
    user = await service.create_user(user_in)
    if not user:
        raise ValidationAPIError(
            message="Email already registered",
            errors=["The email is already registered in the system"],
        )
    return create_response(
        data=user, code=status.HTTP_201_CREATED, message="User created successfully"
    )


@router.get("/me", response_model=Response[UserResponse])
async def read_user_me(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Obtiene el usuario actual."""
    return create_response(
        data=current_user, message="Current user retrieved successfully"
    )


@router.get("/{user_id}", response_model=Response[UserResponse])
async def read_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Obtiene un usuario por su ID."""
    if not current_user.is_superuser and current_user.pkid != user_id:
        raise ValidationAPIError(
            message="Not enough permissions",
            errors=["You don't have permission to access this resource"],
        )

    user = await service.get_user(user_id)
    if not user:
        raise NotFoundError(
            message="User not found", errors=["The requested user does not exist"]
        )
    return create_response(data=user, message="User retrieved successfully")


@router.put("/{user_id}", response_model=Response[UserResponse])
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Actualiza un usuario."""
    if not current_user.is_superuser and current_user.pkid != user_id:
        raise ValidationAPIError(
            message="Not enough permissions",
            errors=["You don't have permission to modify this resource"],
        )

    user = await service.update_user(user_id, user_in)
    if not user:
        raise NotFoundError(
            message="User not found", errors=["The requested user does not exist"]
        )
    return create_response(data=user, message="User updated successfully")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Elimina un usuario."""
    if not current_user.is_superuser and current_user.pkid != user_id:
        raise ValidationAPIError(
            message="Not enough permissions",
            errors=["You don't have permission to delete this resource"],
        )

    if not await service.delete_user(user_id):
        raise NotFoundError(
            message="User not found", errors=["The requested user does not exist"]
        )
    return create_response(
        data=None, code=status.HTTP_204_NO_CONTENT, message="User deleted successfully"
    )
