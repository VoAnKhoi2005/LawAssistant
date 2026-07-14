from typing import List, Dict, Any
from fastapi import HTTPException, status

from repositories.document_repository import DocumentRepository
from repositories.upload_file_repository import UploadFileRepository
from worker.tasks.document_processing_tasks import process_document
from models.document_model import Document


class DocumentService:
    def __init__(self, document_repository: DocumentRepository, upload_file_repository: UploadFileRepository):
        self.document_repository = document_repository
        self.upload_file_repository = upload_file_repository
    
    async def get_all_documents(self, skip: int = 0, limit: int = 100, user_id: str = None) -> List[Document]:
        """Get all documents, optionally filtered by user_id"""
        if user_id:
            # Use repository method to filter by user_id
            document_dicts = await self.document_repository.find_by_user_id(user_id, skip, limit)
        else:
            # Get all documents
            document_dicts = await self.document_repository.find_all(skip, limit)
        
        return [self._dict_to_document(doc_dict) for doc_dict in document_dicts]
    
    async def get_document_by_id(self, document_id: str, user_id: str = None) -> Document:
        """Get document by ID with optional user authorization check"""
        document_dict = await self.document_repository.find_by_id(document_id)
        if not document_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        document = self._dict_to_document(document_dict)
        
        # Check authorization if user_id is provided
        if user_id and document.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this document"
            )
        
        return document
    
    async def get_document_by_so_hieu(self, so_hieu: str, user_id: str = None) -> Document:
        """Get document by so_hieu with optional user authorization check"""
        document_dict = await self.document_repository.find_by_so_hieu(so_hieu)
        if not document_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        document = self._dict_to_document(document_dict)
        
        # Check authorization if user_id is provided
        if user_id and document.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this document"
            )
        
        return document
    
    async def create_document(
        self, 
        so_hieu: str,
        title: str,
        effective_date: str,
        file_ids: List[str],
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Create a document with file references and start processing
        """
        existing_document_dict = await self.document_repository.find_by_so_hieu(so_hieu)
        if existing_document_dict and existing_document_dict.get("user_id") == user_id:
            existing_document = self._dict_to_document(existing_document_dict)
            return {
                "document_id": existing_document.id,
                "task_id": existing_document.task_id,
                "status": existing_document.status or "created",
                "message": "Document already exists; reusing existing processing state",
                "file_refs": [
                    {"file_id": file_ref.file_id, "filename": file_ref.filename}
                    for file_ref in (existing_document.files or [])
                ],
                "metadata": existing_document.model_dump(by_alias=True),
                "reused_existing": True,
            }

        # Validate that all file IDs exist and are uploaded
        file_refs = []
        file_paths = []
        
        for file_id in file_ids:
            file_record = await self.upload_file_repository.find_by_id(file_id)
            if not file_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"File with ID {file_id} not found"
                )
            
            if file_record.get("status") != "uploaded":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file_record.get('filename')} is not in uploaded status"
                )
            
            file_refs.append({
                "file_id": file_id,
                "filename": file_record.get("filename")
            })
            file_paths.append(file_record.get("storage_path"))
        
        # Create Document model instance
        from models.common import DateModel, FileRef
        from datetime import datetime
        
        # Convert file_refs to FileRef objects
        file_ref_objects = [FileRef(file_id=f["file_id"], filename=f["filename"]) for f in file_refs]
        
        # Parse effective_date if it's a string
        parsed_date = datetime.fromisoformat(effective_date) if isinstance(effective_date, str) else effective_date
        
        # Create document model
        document = Document(
            user_id=user_id,
            so_hieu=so_hieu,
            title=title,
            effective_date=DateModel(date=parsed_date),
            is_active=True,
            files=file_ref_objects,
            source_files=file_ref_objects,
            status="created",
            task_id=None,
        )
        
        # Create document in database using the model
        created_document = await self.document_repository.create(document)
        document_id = created_document.id
        
        # Update file statuses to processing
        for file_id in file_ids:
            await self.upload_file_repository.update_status(file_id, "processing")
        
        # Queue processing task
        try:
            task = process_document.delay(
                document_id=document_id,
                file_paths=file_paths,
                metadata=created_document.model_dump(by_alias=True)
            )
            
            # Update document with task ID
            await self.document_repository.update_from_dict(document_id, {
                "task_id": task.id,
                "status": "queued"
            })
            
            return {
                "document_id": document_id,
                "task_id": task.id,
                "status": "queued",
                "message": "Document created and queued for processing",
                "file_refs": file_refs,
                "metadata": created_document.model_dump(by_alias=True)
            }
            
        except Exception as e:
            # Revert file statuses on error
            for file_id in file_ids:
                await self.upload_file_repository.update_status(
                    file_id, "uploaded", f"Processing queue error: {str(e)}"
                )
            
            # Update document status
            await self.document_repository.update_from_dict(document_id, {
                "status": "failed",
                "error": f"Failed to queue processing: {str(e)}"
            })
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to queue document processing: {str(e)}"
            )

    async def recover_pending_documents(self) -> int:
        resumable_statuses = ["created", "queued", "extracting_triplets"]
        pending_documents = await self.document_repository.find_by_statuses(resumable_statuses)
        recovered_count = 0

        for document_dict in pending_documents:
            if await self._requeue_existing_document(document_dict):
                recovered_count += 1

        return recovered_count
    
    async def update_document(self, document_id: str, document: Document, user_id: str = None) -> Document:
        """Update document with optional user authorization check"""
        # Check if document exists and user has permission
        existing_document = await self.get_document_by_id(document_id, user_id)
        
        updated_document = await self.document_repository.update(document_id, document)
        if not updated_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        return updated_document
    
    async def delete_document(self, document_id: str, user_id: str = None) -> bool:
        """Delete document with optional user authorization check"""
        # Check if document exists and user has permission
        await self.get_document_by_id(document_id, user_id)
        
        result = await self.document_repository.delete(document_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        return result

    @staticmethod
    def _dict_to_document(document_dict: dict) -> Document:
        # Convert MongoDB dict to Document model
        document_dict["_id"] = str(document_dict["_id"])
        return Document(**document_dict)

    async def _requeue_existing_document(self, document_dict: dict) -> bool:
        document_id = str(document_dict["_id"])
        files = document_dict.get("files") or document_dict.get("source_files") or []
        if not files:
            return False

        file_paths = []
        file_ids = []
        for file_ref in files:
            file_id = file_ref.get("file_id") if isinstance(file_ref, dict) else getattr(file_ref, "file_id", None)
            if not file_id:
                continue

            file_record = await self.upload_file_repository.find_by_id(file_id)
            if not file_record or not file_record.get("storage_path"):
                continue

            file_ids.append(file_id)
            file_paths.append(file_record["storage_path"])

        if not file_paths:
            return False

        for file_id in file_ids:
            await self.upload_file_repository.update_status(file_id, "processing")

        task = process_document.delay(
            document_id=document_id,
            file_paths=file_paths,
            metadata=self._dict_to_document(document_dict).model_dump(by_alias=True),
        )

        await self.document_repository.update_from_dict(document_id, {
            "task_id": task.id,
            "status": "queued",
        })
        return True
