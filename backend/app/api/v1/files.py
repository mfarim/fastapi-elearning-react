import os
import mimetypes
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.common.storage import storage_service

router = APIRouter(prefix="/files", tags=["File Management"])


@router.get("/{file_path:path}")
async def get_file(file_path: str):
    full_path = storage_service.get_full_path(file_path)
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")

    content_type, _ = mimetypes.guess_type(full_path)
    if not content_type:
        content_type = "application/octet-stream"

    filename = os.path.basename(full_path)
    return FileResponse(
        path=full_path,
        media_type=content_type,
        filename=filename,
        content_disposition_type="inline",
    )
