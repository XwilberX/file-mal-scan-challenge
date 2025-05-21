from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from api.users.router import router as users_router
from api.auth.router import router as auth_router
from api.scans.router import router as scans_router
from core.config import settings
from core.exceptions import (
    APIError,
    api_error_handler,
    http_error_handler,
    python_error_handler,
    validation_error_handler,
)
from core.schemas import create_response

app = FastAPI(
    title="File Malware Scanner API",
    description="API para escanear archivos en busca de malware usando VirusTotal",
    version="0.1.0",
)


# Configuración de seguridad para Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Añadir esquema de seguridad con Bearer
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Ingresa solo tu token JWT (sin el prefijo 'Bearer')",
        }
    }

    # Aplicar seguridad a nivel global para todos los endpoints excepto /auth/token
    for path in openapi_schema["paths"]:
        if not path.endswith("/api/v1/auth/token") and not path == "/":
            for method in openapi_schema["paths"][path]:
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, esto debería ser más restrictivo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejadores de excepciones
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, python_error_handler)

# Incluir routers
app.include_router(users_router, prefix=settings.api_prefix, tags=["users"])
app.include_router(auth_router, prefix=settings.api_prefix, tags=["auth"])
app.include_router(scans_router, prefix=settings.api_prefix, tags=["scans"])


@app.get("/")
async def root():
    """Endpoint raíz para verificar que la API está funcionando."""
    return create_response(
        data={"message": "File Malware Scanner API is running"},
        message="API is running",
    )
