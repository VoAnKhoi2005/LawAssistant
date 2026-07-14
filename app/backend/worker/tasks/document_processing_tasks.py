import logging
from typing import Dict, Any, List
import asyncio

from core.config import settings
from worker.worker import celery_app
from infrastructure.db.database import connect_to_mongo, get_database, close_mongo_connection
from repositories.document_repository import DocumentRepository
from repositories.triplet_repository import TripletRepository
from repositories.concept_repository import ConceptRepository
from repositories.legal_section_repository import LegalSectionRepository
from repositories.relation_repository import RelationRepository
from repositories.upload_file_repository import UploadFileRepository
from services.section_indexing_service import SectionIndexingService
from worker.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

# Module-level cache for heavy NLP models (not DB-dependent)
_nlp_extractor_cache = None
_document_extractor_cache = None
_text_simplifier_cache = None


def get_or_create_infrastructures():
    """Get cached NLP models or create new ones if not exists"""
    global _nlp_extractor_cache, _document_extractor_cache, _text_simplifier_cache
    
    if _nlp_extractor_cache is None:
        from infrastructure.document_processing.document_extraction.google_cloud_extractor import GoogleCloudDocumentExtractor
        from infrastructure.document_processing.text_simplification.openai_simplifier import OpenAITextSimplifier
        from infrastructure.document_processing.triplet_extraction.nlp_extractor import NLPTripletExtractor
        
        logger.info("Initializing NLP models (first time - this may take a moment)")
        
        _document_extractor_cache = GoogleCloudDocumentExtractor(
            credential_file=settings.google_application_credentials,
            bucket_name=settings.google_cloud_storage_bucket
        )
        
        _text_simplifier_cache = OpenAITextSimplifier(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )
        
        _nlp_extractor_cache = NLPTripletExtractor(
            vncorenlp_dir=settings.vncorenlp_model_path,
            phonlp_dir=settings.phonlp_model_path,
        )
        
        logger.info("NLP models initialized successfully")
    
    return _document_extractor_cache, _text_simplifier_cache, _nlp_extractor_cache


def create_document_processor(db):
    """Create processor with fresh DB connections but cached NLP models"""
    # Get cached NLP models (heavy, loaded once)
    document_extractor, text_simplifier, triplet_extractor = get_or_create_infrastructures()
    
    # Create fresh repositories with current DB connection
    document_repo = DocumentRepository(db)
    triplet_repo = TripletRepository(db)
    concept_repo = ConceptRepository(db)
    legal_section_repo = LegalSectionRepository(db)
    relation_repo = RelationRepository(db)
    upload_file_repo = UploadFileRepository(db)
    section_indexing_service = SectionIndexingService(
        legal_section_repository=legal_section_repo,
        semantic_index_dir="/app/pipeline/retrieval/semantic/search_index",
    )

    # Create processor with fresh DB dependencies but cached models
    processor = DocumentProcessor(
        document_repository=document_repo,
        triplet_repository=triplet_repo,
        concept_repository=concept_repo,
        section_indexing_service=section_indexing_service,
        relation_repository=relation_repo,
        upload_file_repository=upload_file_repo,
        document_extractor=document_extractor,
        text_simplifier=text_simplifier,
        triplet_extractor=triplet_extractor
    )

    return processor


async def run_document_processing(document_id: str, file_paths: List[str], metadata: Dict[str, Any], progress_callback):
    """Run Mongo initialization and document processing on the same event loop."""
    try:
        await connect_to_mongo()
        db = get_database()
        processor = create_document_processor(db)
        return await processor.process_document_pipeline(
            document_id=document_id,
            file_paths=file_paths,
            metadata=metadata,
            progress_callback=progress_callback,
        )
    finally:
        await close_mongo_connection()


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def process_document(self, document_id: str, file_paths: List[str], metadata: Dict[str, Any]):
    """Orchestrates document processing pipeline using DocumentProcessor"""

    def update(step: str, progress: int):
        """Helper to update task state"""
        self.update_state(
            state="PROCESSING",
            meta={
                "step": step,
                "progress": progress,
                "document_id": document_id
            }
        )

    try:
        logger.info(f"[START] Processing document {document_id}")
        update("Starting document processing", 0)

        result = asyncio.run(
            run_document_processing(
                document_id=document_id,
                file_paths=file_paths,
                metadata=metadata,
                progress_callback=update,
            )
        )

        logger.info(f"[DONE] Document {document_id}")

        return {
            "status": "completed",
            "document_id": document_id,
            "stats": result
        }

    except Exception as e:
        logger.exception(f"[ERROR] Document {document_id}")

        self.update_state(
            state="FAILURE",
            meta={
                "step": "Processing failed",
                "error": str(e),
                "document_id": document_id
            }
        )

        raise
