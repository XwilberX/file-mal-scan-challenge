from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from .models import ScanStatus


class ScanResponse(BaseModel):
    """Esquema para la respuesta de un escaneo."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "pkid": 1,
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
                "created_at": "2024-03-21T12:00:00Z",
                "updated_at": "2024-03-21T12:05:00Z",
                "detailed_report": {
                    "attributes": {
                        "type_description": "Win32 EXE",
                        "size": 1024,
                        "last_analysis_stats": {
                            "malicious": 5,
                            "suspicious": 2,
                            "undetected": 53,
                        },
                        "last_analysis_results": {
                            "antivirus1": {
                                "category": "malicious",
                                "result": "Trojan.Win32.Generic",
                            }
                        },
                    }
                },
            }
        },
    )

    pkid: int
    filename: str
    original_filename: str
    file_size: int  # Tamaño en bytes
    file_type: str
    md5_hash: str
    sha1_hash: str
    sha256_hash: str
    status: ScanStatus
    scan_id: Optional[str] = None
    scan_date: Optional[datetime] = None
    result_date: Optional[datetime] = None
    positives: Optional[int] = None
    total_scans: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    detailed_report: Optional[dict[str, Any]] = None


class ScanCreate(BaseModel):
    """Esquema para crear un nuevo escaneo."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "malware_sample.exe",
                "file_size": 1024,
                "file_type": "application/x-msdownload",
                "md5_hash": "d41d8cd98f00b204e9800998ecf8427e",
                "sha1_hash": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
                "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            }
        }
    )

    filename: str
    original_filename: str
    file_size: int
    file_type: str
    md5_hash: str
    sha1_hash: str
    sha256_hash: str
