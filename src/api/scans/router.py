from typing import Annotated, List

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlmodel.ext.asyncio.session import AsyncSession

from api.auth.router import get_current_user
from core.config import settings
from core.database import get_session
from core.exceptions import NotFoundError, ValidationAPIError
from core.schemas import Response, create_response
from .models import FileScan
from .schemas import ScanResponse
from .service import ScanService

router = APIRouter(prefix="/scans", tags=["scans"])


async def get_scan_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ScanService:
    """Dependencia para obtener el servicio de escaneos."""
    return ScanService(session)


@router.post(
    "/upload",
    response_model=Response[ScanResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    file: Annotated[UploadFile, File()],
    service: Annotated[ScanService, Depends(get_scan_service)],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Sube un archivo para ser analizado."""
    scan = await service.save_uploaded_file(file, current_user.pkid)
    if not scan:
        raise ValidationAPIError(
            message="Invalid file",
            errors=[
                "File type not allowed or file too large",
                f"Allowed extensions: {', '.join(sorted(settings.ALLOWED_EXTENSIONS))}",
            ],
        )

    # Enviar a VirusTotal
    if not await service.submit_to_virustotal(scan, file):
        raise ValidationAPIError(
            message="Error submitting file",
            errors=["Could not submit file to VirusTotal"],
        )

    return create_response(
        data=scan,
        code=status.HTTP_201_CREATED,
        message="File uploaded and submitted for analysis",
    )


@router.get("/{scan_id}", response_model=Response[ScanResponse])
async def get_scan(
    scan_id: int,
    service: Annotated[ScanService, Depends(get_scan_service)],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Obtiene el resultado de un escaneo."""
    scan = await service.get_scan(scan_id, current_user.pkid)
    if not scan:
        raise NotFoundError(
            message="Scan not found", errors=["The requested scan does not exist"]
        )

    # Si está en proceso, intentar obtener resultados
    if scan.status == "scanning":
        await service.get_scan_results(scan)
        # Recargar el escaneo para obtener los resultados actualizados
        scan = await service.get_scan(scan_id, current_user.pkid)

    # Si está completado, obtener el reporte detallado
    detailed_report = None
    if scan.status == "completed":
        detailed_report = await service.get_file_report(scan)

    # Crear respuesta con el reporte detallado si está disponible
    response_data = ScanResponse.model_validate(scan)
    if detailed_report:
        response_data.detailed_report = detailed_report

    return create_response(
        data=response_data, message="Scan results retrieved successfully"
    )


@router.get("/", response_model=Response[List[ScanResponse]])
async def list_scans(
    service: Annotated[ScanService, Depends(get_scan_service)],
    current_user: Annotated[dict, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    """Lista los escaneos del usuario."""
    scans = await service.list_user_scans(
        user_id=current_user.pkid, skip=skip, limit=limit
    )
    return create_response(data=scans, message="Scans retrieved successfully")
