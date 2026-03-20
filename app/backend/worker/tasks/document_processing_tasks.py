"""
Document processing tasks for Celery worker
"""
import logging
from typing import Dict, Any

from worker.worker import celery_app
from worker.document_processor import process_document_pipeline

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def process_document(self, document_id: str, file_path: str, metadata: Dict[str, Any]):
    """Orchestrates document processing pipeline"""

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

        result = process_document_pipeline(
            document_id=document_id,
            file_path=file_path,
            metadata=metadata,
            progress_callback=update
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