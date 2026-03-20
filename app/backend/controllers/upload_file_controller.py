from typing import List
from fastapi import UploadFile

from services.upload_file_service import UploadFileService
from dto.upload_file_dto import UpdateFileStatusRequest


class UploadFileController:
    def __init__(self, upload_file_service: UploadFileService):
        self.upload_file_service = upload_file_service
    
    async def get_all(self, skip: int = 0, limit: int = 100, user_id: str = None):
        """Get all files, optionally filtered by user_id"""
        return await self.upload_file_service.get_all_files(skip, limit, user_id)
    
    async def get_by_id(self, file_id: str, user_id: str = None):
        """Get file by ID with optional authorization check"""
        return await self.upload_file_service.get_file_by_id(file_id, user_id)
    
    async def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100):
        """Get files for a specific user"""
        return await self.upload_file_service.get_files_by_user_id(user_id, skip, limit)
    
    async def get_by_status(self, status: str, skip: int = 0, limit: int = 100, user_id: str = None):
        """Get files by status, optionally filtered by user_id"""
        files = await self.upload_file_service.get_files_by_status(status, skip, limit)
        # Filter by user_id if provided
        if user_id:
            files = [f for f in files if f.user_id == user_id]
        return files
    
    async def upload_file(self, file: UploadFile, user_id: str):
        """Upload file with user_id from JWT token"""
        return await self.upload_file_service.upload_file(file, user_id)
    
    async def upload_multiple_files(self, files: List[UploadFile], user_id: str):
        """Upload multiple files with user_id from JWT token"""
        return await self.upload_file_service.upload_multiple_files(files, user_id)
    
    async def update_status(self, file_id: str, request: UpdateFileStatusRequest, user_id: str = None):
        """Update file status with authorization check"""
        return await self.upload_file_service.update_file_status(
            file_id, 
            request.status, 
            request.error,
            user_id
        )
    
    async def delete(self, file_id: str, user_id: str = None):
        """Delete file with authorization check"""
        await self.upload_file_service.delete_file(file_id, user_id)
        return {"message": "File deleted successfully"}
    
    async def download(self, file_id: str, user_id: str = None):
        """Download file with authorization check"""
        return await self.upload_file_service.get_file_content(file_id, user_id)