import secrets
from pathlib import Path
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Obtener la ruta absoluta al directorio raíz del proyecto
ROOT_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Settings para la app."""

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_ignore_empty=True,
        extra="ignore",
    )

    API_VERSION: str = "v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    PROJECT_NAME: str = "File Malware Scanner"

    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "file_scanner"
    DB_ECHO: bool = False

    # VirusTotal settings
    VIRUSTOTAL_API_KEY: str
    VIRUSTOTAL_API_URL: str = "https://www.virustotal.com/api/v3"

    # File upload settings
    MAX_FILE_SIZE: int = 32  # MB
    ALLOWED_EXTENSIONS: list[str] = [
        # Ejecutables
        "exe",
        "dll",
        "sys",
        # Scripts
        "js",
        "py",
        "php",
        "sh",
        "bat",
        # Documentos
        "pdf",
        "doc",
        "docx",
        "xls",
        "xlsx",
        # Comprimidos
        "zip",
        "rar",
        "7z",
        "tar",
        "gz",
    ]

    @computed_field
    @property
    def DATABASE_URI(self) -> str:
        """Construye la URI de conexión a la base de datos."""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @computed_field
    @property
    def api_prefix(self) -> str:
        """Helper para constuir prefix para los path`s de los endpoints."""
        return f"/api/{self.API_VERSION}"


settings = Settings()  # type: ignore
