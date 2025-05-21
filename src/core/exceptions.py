from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .schemas import create_error


class APIError(HTTPException):
    """Excepción base para errores de la API."""

    def __init__(
        self, status_code: int, message: str, errors: Optional[list[str]] = None
    ) -> None:
        """Inicializa la excepción."""
        super().__init__(status_code=status_code, detail=message)
        self.errors = errors


class NotFoundError(APIError):
    """Error para recursos no encontrados."""

    def __init__(
        self, message: str = "Resource not found", errors: Optional[list[str]] = None
    ) -> None:
        """Inicializa la excepción."""
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, message=message, errors=errors
        )


class ValidationAPIError(APIError):
    """Error para validación de datos."""

    def __init__(
        self, message: str = "Validation error", errors: Optional[list[str]] = None
    ) -> None:
        """Inicializa la excepción."""
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            errors=errors,
        )


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Manejador para errores de la API."""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error(
            code=exc.status_code, message=str(exc.detail), errors=exc.errors
        ).model_dump(),
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Manejador para errores de validación."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = f"{field}: {error['msg']}"
        errors.append(message)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation error",
            errors=errors,
        ).model_dump(),
    )


async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Manejador para errores HTTP genéricos."""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error(
            code=exc.status_code, message=str(exc.detail)
        ).model_dump(),
    )


async def python_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Manejador para errores de Python no manejados."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
            errors=[str(exc)],
        ).model_dump(),
    )
