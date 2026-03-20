import os
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any, Coroutine
from fastapi import HTTPException, UploadFile, status

from repositories.upload_file_repository import UploadFileRepository
from models.uploaded_file_model import UploadedFile


class UploadFileService:
    def __init__(self, upload_file_repository: UploadFileRepository):
        self.upload_file_repository = upload_file_repository
        self.uploads_dir = Path("uploads")
        self.uploads_dir.mkdir(exist_ok=True)
    
    async def get_all_files(self, skip: int = 0, limit: int = 100, user_id: str = None) -> List[UploadedFile]:
        """Get all files, optionally filtered by user_id"""
        if user_id:
            # Use repository method to filter by user_id
            file_dicts = await self.upload_file_repository.find_by_user_id(user_id, skip, limit)
        else:
            # Get all files
            file_dicts = await self.upload_file_repository.find_all(skip, limit)
        
        return [self._dict_to_uploaded_file(file_dict) for file_dict in file_dicts]
    
    async def get_file_by_id(self, file_id: str, user_id: str = None) -> UploadedFile:
        """Get file by ID with optional user authorization check"""
        file_dict = await self.upload_file_repository.find_by_id(file_id)
        if not file_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        uploaded_file = self._dict_to_uploaded_file(file_dict)
        
        # Check authorization if user_id is provided
        if user_id and uploaded_file.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this file"
            )
        
        return uploaded_file
    
    async def get_files_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[UploadedFile]:
        file_dicts = await self.upload_file_repository.find_by_user_id(user_id, skip, limit)
        return [self._dict_to_uploaded_file(file_dict) for file_dict in file_dicts]
    
    async def get_files_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[UploadedFile]:
        file_dicts = await self.upload_file_repository.find_by_status(status, skip, limit)
        return [self._dict_to_uploaded_file(file_dict) for file_dict in file_dicts]
    
    async def upload_file(self, file: UploadFile, user_id: str) -> dict:
        """
        Upload a single file and save metadata to database
        """
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File name is required"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        unique_filename = f"{file_id}{file_extension}"
        
        # Create user-specific directory
        user_upload_dir = self.uploads_dir / user_id
        user_upload_dir.mkdir(exist_ok=True)
        
        # Save file to filesystem
        file_path = user_upload_dir / unique_filename
        try:
            content = await file.read()
            with open(file_path, "wb") as buffer:
                buffer.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
        
        # Prepare file metadata
        uploaded_file = UploadedFile(
            user_id=user_id,
            file_id=file_id,
            filename=file.filename,
            storage_path=str(file_path),
            content_type=file.content_type,
            size=len(content),
            status="uploaded"
        )
        
        # Save metadata to database
        try:
            return await self.upload_file_repository.create_from_dict({
                "user_id": user_id,
                "file_id": file_id,
                "filename": file.filename,
                "storage_path": str(file_path),
                "content_type": file.content_type,
                "size": len(content),
                "status": "uploaded"
            })
        except Exception as e:
            # Clean up file if database save fails
            if file_path.exists():
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file metadata: {str(e)}"
            )
    
    async def upload_multiple_files(self, files: List[UploadFile], user_id: str) -> dict[str, list[Any] | str] | list[
        Any]:
        """
        Upload multiple files
        """
        uploaded_files = []
        failed_files = []
        
        for file in files:
            try:
                uploaded_file = await self.upload_file(file, user_id)
                uploaded_files.append(uploaded_file)
            except HTTPException as e:
                failed_files.append({
                    "filename": file.filename,
                    "error": e.detail
                })
        
        if failed_files:
            # If some files failed, still return success for uploaded files
            # but include error information
            return {
                "uploaded_files": uploaded_files,
                "failed_files": failed_files,
                "message": f"Uploaded {len(uploaded_files)} files, {len(failed_files)} failed"
            }
        
        return uploaded_files
    
    async def update_file_status(self, file_id: str, status: str, error: Optional[str] = None, user_id: str = None) -> dict:
        """
        Update file processing status with optional authorization check
        """
        # Check authorization if user_id is provided
        if user_id:
            await self.get_file_by_id(file_id, user_id)
        
        file_record = await self.upload_file_repository.update_status(file_id, status, error)
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        return file_record
    
    async def delete_file(self, file_id: str, user_id: str = None) -> bool:
        """
        Delete file from both filesystem and database with authorization check
        """
        # Get file record first and check authorization
        file_dict = await self.upload_file_repository.find_by_id(file_id)
        if not file_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        uploaded_file = self._dict_to_uploaded_file(file_dict)
        
        # Check authorization if user_id is provided
        if user_id and uploaded_file.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this file"
            )
        
        # Delete from filesystem
        file_path = Path(file_dict["storage_path"])
        if file_path.exists():
            try:
                os.remove(file_path)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to delete file from filesystem: {str(e)}"
                )
        
        # Delete from database
        result = await self.upload_file_repository.delete(file_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return result
    
    async def get_file_content(self, file_id: str, user_id: str = None) -> tuple[bytes, str, str]:
        """
        Get file content for download with authorization check
        Returns: (file_content, filename, content_type)
        """
        # Get file and check authorization
        file_dict = await self.upload_file_repository.find_by_id(file_id)
        if not file_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        uploaded_file = self._dict_to_uploaded_file(file_dict)
        
        # Check authorization if user_id is provided
        if user_id and uploaded_file.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to download this file"
            )
        
        file_path = Path(file_dict["storage_path"])
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on filesystem"
            )
        
        try:
            with open(file_path, "rb") as file:
                content = file.read()
            
            return (
                content, 
                file_dict["filename"], 
                file_dict.get("content_type", "application/octet-stream")
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read file: {str(e)}"
            )

    @staticmethod
    def _dict_to_uploaded_file(file_dict: dict) -> UploadedFile:
        # Convert MongoDB dict to UploadedFile model
        file_dict["_id"] = str(file_dict["_id"])
        return UploadedFile(**file_dict)