from services.document_service import DocumentService
from dto.document_dto import CreateDocumentRequest, UpdateDocumentRequest


class DocumentController:
    def __init__(self, document_service: DocumentService):
        self.document_service = document_service
    
    async def get_all(self, skip: int = 0, limit: int = 100, user_id: str = None):
        """Get all documents, optionally filtered by user_id"""
        return await self.document_service.get_all_documents(skip, limit, user_id)
    
    async def get_by_id(self, document_id: str, user_id: str = None):
        """Get document by ID with optional authorization check"""
        return await self.document_service.get_document_by_id(document_id, user_id)
    
    async def get_by_so_hieu(self, so_hieu: str, user_id: str = None):
        """Get document by so_hieu with optional authorization check"""
        return await self.document_service.get_document_by_so_hieu(so_hieu, user_id)
    
    async def create(self, request: CreateDocumentRequest, user_id: str):
        """Create document with user_id from JWT token"""
        return await self.document_service.create_document(
            so_hieu=request.so_hieu,
            title=request.title,
            effective_date=request.effective_date,
            file_ids=request.file_ids,
            user_id=user_id,
        )
    
    async def update(self, document_id: str, request: UpdateDocumentRequest, user_id: str = None):
        """Update document with authorization check"""
        # Convert request to Document model
        from models.document_model import Document
        document_data = request.model_dump(by_alias=True, exclude_unset=True)
        # Note: This is a partial update, so we need to fetch the existing document first
        existing_document = await self.document_service.get_document_by_id(document_id, user_id)
        
        # Merge updates
        updated_data = existing_document.model_dump()
        updated_data.update(document_data)
        updated_document = Document(**updated_data)
        
        return await self.document_service.update_document(document_id, updated_document, user_id)
    
    async def delete(self, document_id: str, user_id: str = None):
        """Delete document with authorization check"""
        await self.document_service.delete_document(document_id, user_id)
        return {"message": "Document deleted successfully"}
