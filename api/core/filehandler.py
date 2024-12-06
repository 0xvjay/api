import os
import uuid
from pathlib import Path
from typing import List

from fastapi import HTTPException, UploadFile


class FileHandler:
    """
    A class to handle file uploads in chunks with file type validation
    """

    def __init__(
        self,
        base_directory: str,
        allowed_extensions: List[str] | None = None,
        chunk_size: int = 1024 * 1024,
    ):
        """
        Initialize FileHandler

        Args:
            base_directory (str): Base directory for file storage
            allowed_extensions (List[str], optional): List of allowed file extensions (e.g., ['.png', '.jpg'])
            chunk_size (int): Size of chunks in bytes (default 1MB)
        """
        self.base_directory = Path(base_directory)
        self.chunk_size = chunk_size
        self.allowed_extensions = [
            ext.lower() if ext.startswith(".") else f".{ext.lower()}"
            for ext in (allowed_extensions or [])
        ]

        os.makedirs(self.base_directory, exist_ok=True)

    def _validate_file_type(self, filename: str) -> bool:
        """
        Validate if file extension is allowed

        Args:
            filename (str): Name of the file to validate

        Returns:
            bool: True if file type is allowed or no restrictions set
        """
        if not self.allowed_extensions:
            return True

        file_extension = os.path.splitext(filename)[1].lower()
        return file_extension in self.allowed_extensions

    async def save_file(self, file: UploadFile, subdirectory: str | None = None) -> str:
        """
        Save file in chunks to specified directory

        Args:
            file (UploadFile): FastAPI UploadFile object
            subdirectory (str, optional): Subdirectory within base directory

        Returns:
            str: Path to saved file

        Raises:
            HTTPException: If file type is not allowed
        """
        if not self._validate_file_type(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(self.allowed_extensions)}",
            )

        unique_filename = f"{uuid.uuid4()}_{file.filename}"

        if subdirectory:
            save_dir = self.base_directory / subdirectory
            os.makedirs(save_dir, exist_ok=True)
        else:
            save_dir = self.base_directory

        file_path = save_dir / unique_filename

        try:
            with open(file_path, "wb") as buffer:
                while True:
                    chunk = await file.read(self.chunk_size)
                    if not chunk:
                        break
                    buffer.write(chunk)

            return str(file_path)

        except Exception as e:
            if file_path.exists():
                os.remove(file_path)
            raise Exception(f"Failed to save file: {str(e)}")

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file

        Args:
            file_path (str): Path to file to delete

        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
