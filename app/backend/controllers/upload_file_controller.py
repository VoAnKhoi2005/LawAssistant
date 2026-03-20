from typing import List
from fastapi import UploadFile

from services.upload_file_service import UploadFileService
from dto.upload_file_dto import UpdateFileStatusRequest


class UploadFileController:
    def __init__(self, upload_file_service: UploadFileService):
        self.upload_file_service = upload_file_service
    
    async def get_all(self, skip: int = 0, limit: int = 100):
        return await self.upload_file_service.get_all_files(skip, limit)
    
    async def get_by_id(self, file_id: str):
        return await self.upload_file_service.get_file_by_id(file_id)
    
    async def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100):
        return await self.upload_file_service.get_files_by_user_id(user_id, skip, limit)
    
    async def get_by_status(self, status: str, skip: int = 0, limit: int = 100):
        return await self.upload_file_service.get_files_by_status(status, skip, limit)
    
    async def upload_file(self, file: UploadFile, user_id: str):
        return await self.upload_file_service.upload_file(file, user_id)
    
    async def upload_multiple_files(self, files: List[UploadFile], user_id: str):
        return await self.upload_file_service.upload_multiple_files(files, user_id)
    
    async def update_status(self, file_id: str, request: UpdateFileStatusRequest):
        return await self.upload_file_service.update_file_status(
            file_id, request.status, request.error
        )
    
    async def delete(self, file_id: str):
        await self.upload_file_service.delete_file(file_id)
        return {"message": "File deleted successfully"}
    
    async def download(self, file_id: str):
        return await self.upload_file_service.get_file_content(file_id)