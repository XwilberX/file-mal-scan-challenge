from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict


class Status(BaseModel):
    """Modelo para el estado de la respuesta."""

    code: int
    message: str

    model_config = ConfigDict(
        json_schema_extra={"example": {"code": 200, "message": "Request succeeded"}}
    )


T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """Modelo base para respuestas exitosas."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "status": {"code": 200, "message": "Request succeeded"},
                "data": {"id": 1, "name": "Example Data"},
            }
        },
    )

    status: Status
    data: T


class ErrorResponse(BaseModel):
    """Modelo para respuestas de error."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": {"code": 404, "message": "Resource not found"},
                "errors": ["The requested resource could not be found."],
            }
        }
    )

    status: Status
    errors: List[str]


def create_response(
    data: Any, code: int = 200, message: str = "Request succeeded"
) -> Response:
    """Crea una respuesta exitosa estandarizada."""
    return Response(status=Status(code=code, message=message), data=data)


def create_error(
    code: int, message: str, errors: Optional[List[str]] = None
) -> ErrorResponse:
    """Crea una respuesta de error estandarizada."""
    return ErrorResponse(
        status=Status(code=code, message=message), errors=errors or [message]
    )
