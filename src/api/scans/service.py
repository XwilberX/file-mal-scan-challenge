import hashlib
from pathlib import Path
from typing import Optional

import httpx
from fastapi import UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession

from core.config import settings
from core.models import get_utc_now
from .models import FileScan, ScanStatus
from .repository import ScanRepository


class ScanService:
    """Servicio para el escaneo de archivos."""

    def __init__(self, session: AsyncSession):
        """Inicializa el servicio."""
        self.session = session
        self.repository = ScanRepository(session)

    async def _calculate_file_hashes(self, file: UploadFile) -> tuple[str, str, str]:
        """Calcula los hashes MD5, SHA1 y SHA256 de un archivo."""
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()

        # Leer el archivo en chunks sin guardarlo
        while chunk := await file.read(8192):
            md5.update(chunk)
            sha1.update(chunk)
            sha256.update(chunk)

        # Regresar el archivo al inicio para futuras lecturas
        await file.seek(0)
        return md5.hexdigest(), sha1.hexdigest(), sha256.hexdigest()

    def _get_file_extension(self, filename: str) -> str:
        """Obtiene la extensión de un archivo."""
        extension = Path(filename).suffix.lower().lstrip(".")
        return extension

    async def save_uploaded_file(
        self, file: UploadFile, user_id: int
    ) -> Optional[FileScan]:
        """Procesa un archivo subido y crea un registro de escaneo."""
        if not file.filename:
            return None

        # Verificar extensión
        extension = self._get_file_extension(file.filename)
        allowed_extensions = list(settings.ALLOWED_EXTENSIONS)
        if extension not in allowed_extensions:
            return None

        try:
            # Verificar tamaño mientras calculamos hashes
            file_size = 0
            md5 = hashlib.md5()
            sha1 = hashlib.sha1()
            sha256 = hashlib.sha256()

            # Asegurarnos de empezar desde el inicio
            await file.seek(0)

            # Leer el archivo una sola vez
            content = await file.read()
            file_size = len(content)

            if file_size > settings.MAX_FILE_SIZE * 1024 * 1024:  # Convertir MB a bytes
                return None

            # Calcular hashes
            md5.update(content)
            sha1.update(content)
            sha256.update(content)

            # Regresar el archivo al inicio para el envío a VirusTotal
            await file.seek(0)

            # Crear registro
            scan_data = {
                "filename": file.filename,  # Usamos el nombre original
                "original_filename": file.filename,
                "file_size": file_size,  # Guardamos en bytes
                "file_type": file.content_type or "application/octet-stream",
                "md5_hash": md5.hexdigest(),
                "sha1_hash": sha1.hexdigest(),
                "sha256_hash": sha256.hexdigest(),
                "user_id": user_id,
            }

            return await self.repository.create(obj_in=scan_data)

        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return None

    async def submit_to_virustotal(self, scan: FileScan, file: UploadFile) -> bool:
        """Envía un archivo a VirusTotal para su análisis."""
        headers = {
            "x-apikey": settings.VIRUSTOTAL_API_KEY,
            "accept": "application/json",
        }

        try:
            # Asegurarnos de que el archivo esté al inicio
            await file.seek(0)
            file_content = await file.read()

            async with httpx.AsyncClient() as client:
                # Determinar el endpoint según el tamaño del archivo
                if scan.file_size <= 32 * 1024 * 1024:  # 32MB en bytes
                    # Subida directa para archivos pequeños
                    files = {"file": (scan.original_filename, file_content)}
                    response = await client.post(
                        f"{settings.VIRUSTOTAL_API_URL}/files",
                        headers=headers,
                        files=files,
                    )
                    if response.status_code != 200:
                        print(
                            f"Error submitting file to VirusTotal: {response.status_code}"
                        )
                        return False
                    result = response.json()
                else:
                    # Obtener URL para subida de archivos grandes
                    response = await client.get(
                        f"{settings.VIRUSTOTAL_API_URL}/files/upload_url",
                        headers=headers,
                    )
                    if response.status_code != 200:
                        print(f"Error getting upload URL: {response.status_code}")
                        return False
                    upload_url = response.json()["data"]

                    # Subir archivo grande
                    files = {"file": (scan.original_filename, file_content)}
                    response = await client.post(
                        upload_url, headers=headers, files=files
                    )
                    if response.status_code != 200:
                        print(f"Error uploading large file: {response.status_code}")
                        return False
                    result = response.json()

                scan_id = result["data"]["id"]

            # Actualizar registro
            await self.repository.update(
                db_obj=scan,
                obj_in={
                    "status": ScanStatus.SCANNING,
                    "scan_id": scan_id,
                    "scan_date": get_utc_now(),
                },
            )
            return True

        except Exception as e:
            print(f"Error in submit_to_virustotal: {str(e)}")
            return False

    async def get_scan_results(self, scan: FileScan) -> bool:
        """Obtiene los resultados del análisis de VirusTotal."""
        if not scan.scan_id:
            return False

        headers = {
            "x-apikey": settings.VIRUSTOTAL_API_KEY,
            "accept": "application/json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.VIRUSTOTAL_API_URL}/analyses/{scan.scan_id}",
                    headers=headers,
                )
                if response.status_code != 200:
                    return False

                result = response.json()
                attributes = result["data"]["attributes"]
                stats = attributes["stats"]

                # Actualizar registro
                await self.repository.update(
                    db_obj=scan,
                    obj_in={
                        "status": ScanStatus.COMPLETED,
                        "result_date": get_utc_now(),
                        "positives": stats["malicious"],
                        "total_scans": sum(stats.values()),
                    },
                )
                return True

        except Exception:
            return False

    async def get_file_report(self, scan: FileScan) -> Optional[dict]:
        """Obtiene el reporte detallado de un archivo desde VirusTotal usando su hash."""
        if scan.status != ScanStatus.COMPLETED:
            return None

        headers = {
            "x-apikey": settings.VIRUSTOTAL_API_KEY,
            "accept": "application/json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.VIRUSTOTAL_API_URL}/files/{scan.sha256_hash}",
                    headers=headers,
                )
                if response.status_code != 200:
                    return None

                return response.json()["data"]

        except Exception:
            return None

    async def get_scan(self, scan_id: int, user_id: int) -> Optional[FileScan]:
        """Obtiene un escaneo por su ID."""
        scan = await self.repository.get(scan_id)
        if not scan or scan.user_id != user_id:
            return None
        return scan

    async def list_user_scans(
        self, user_id: int, skip: int = 0, limit: int = 10
    ) -> list[FileScan]:
        """Lista los escaneos de un usuario."""
        return await self.repository.get_multi(
            skip=skip, limit=limit, filters={"user_id": user_id}
        )
