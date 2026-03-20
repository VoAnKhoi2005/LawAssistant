from services.document_service import DocumentService
from dto.document_dto import CreateDocumentRequest, UpdateDocumentRequest


class DocumentController:
    def __init__(self, document_service: DocumentService):
        self.document_service = document_service
    
    async def get_all(self, skip: int = 0, limit: int = 100):
        return await self.document_service.get_all_documents(skip, limit)
    
    async def get_by_id(self, document_id: str):
        return await self.document_service.get_document_by_id(document_id)
    
    async def get_by_so_hieu(self, so_hieu: str):
        return await self.document_service.get_document_by_so_hieu(so_hieu)
    
    async def create(self, request: CreateDocumentRequest):
        document_data = request.model_dump(by_alias=True)
        return await self.document_service.create_document(document_data)
    
    async def update(self, document_id: str, request: UpdateDocumentRequest):
        document_data = request.model_dump(by_alias=True, exclude_unset=True)
        return await self.document_service.update_document(document_id, document_data)
    
    async def delete(self, document_id: str):
        await self.document_service.delete_document(document_id)
        return {"message": "Document deleted successfully"}
