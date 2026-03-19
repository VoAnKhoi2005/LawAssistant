from typing import List, Optional
from repositories.document_repository import DocumentRepository
from fastapi import HTTPException, status


class DocumentService:
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository
    
    async def get_all_documents(self, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.document_repository.find_all(skip, limit)
    
    async def get_document_by_id(self, document_id: str) -> dict:
        document = await self.document_repository.find_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        return document
    
    async def get_document_by_so_hieu(self, so_hieu: str) -> dict:
        document = await self.document_repository.find_by_so_hieu(so_hieu)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        return document
    
    async def create_document(self, document_data: dict) -> dict:
        return await self.document_repository.create(document_data)
    
    async def update_document(self, document_id: str, document_data: dict) -> dict:
        document = await self.document_repository.update(document_id, document_data)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        return document
    
    async def delete_document(self, document_id: str) -> bool:
        result = await self.document_repository.delete(document_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        return result
