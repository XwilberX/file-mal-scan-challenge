from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field

from core.models import BaseModel


class ScanStatus(str, Enum):
    """Estados posibles de un escaneo."""

    PENDING = "pending"
    SCANNING = "scanning"
    COMPLETED = "completed"
    ERROR = "error"


class FileScan(BaseModel, table=True):
    """Modelo para almacenar información de escaneos de archivos."""

    filename: str = Field(index=True)
    original_filename: str
    file_size: int = Field(description="Tamaño del archivo en bytes")
    file_type: str
    md5_hash: str = Field(index=True)
    sha1_hash: str = Field(index=True)
    sha256_hash: str = Field(index=True)
    status: ScanStatus = Field(default=ScanStatus.PENDING)
    scan_id: Optional[str] = Field(default=None)
    scan_date: Optional[datetime] = Field(default=None)
    result_date: Optional[datetime] = Field(default=None)
    positives: Optional[int] = Field(default=None)
    total_scans: Optional[int] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    user_id: int = Field(foreign_key="user.pkid", index=True)

    class Config:
        """Configuración del modelo."""

        json_schema_extra = {
            "example": {
                "filename": "malware_sample.exe",
                "original_filename": "sample.exe",
                "file_size": 0.001,  # Tamaño en MB
                "file_type": "application/x-msdownload",
                "md5_hash": "d41d8cd98f00b204e9800998ecf8427e",
                "sha1_hash": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
                "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "status": "completed",
                "scan_id": "1234567890",
                "scan_date": "2024-03-21T12:00:00Z",
                "result_date": "2024-03-21T12:05:00Z",
                "positives": 5,
                "total_scans": 60,
            }
        }
