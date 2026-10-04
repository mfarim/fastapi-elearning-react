import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings


class FileStorageService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_file(self, file: UploadFile, subfolder: str = "attachments") -> str:
        target_dir = os.path.join(self.upload_dir, subfolder)
        os.makedirs(target_dir, exist_ok=True)

        original_ext = Path(file.filename).suffix if file.filename else ""
        unique_name = f"{uuid.uuid4().hex}{original_ext}"
        target_path = os.path.join(target_dir, unique_name)

        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Return relative storage path
        return f"{subfolder}/{unique_name}"

    def get_full_path(self, relative_path: str) -> str:
        return os.path.join(self.upload_dir, relative_path)

    def file_exists(self, relative_path: str) -> bool:
        full_path = self.get_full_path(relative_path)
        return os.path.isfile(full_path)


storage_service = FileStorageService()
