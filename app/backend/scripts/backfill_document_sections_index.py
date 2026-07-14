import argparse
import asyncio
from pathlib import Path

from core.config import settings
from infrastructure.db.database import close_mongo_connection, connect_to_mongo, get_database
from infrastructure.document_processing.document_extraction.google_cloud_extractor import (
    GoogleCloudDocumentExtractor,
)
from repositories.document_repository import DocumentRepository
from repositories.legal_section_repository import LegalSectionRepository
from services.section_indexing_service import SectionIndexingService


async def main(document_id: str, file_path: str) -> int:
    await connect_to_mongo()
    try:
        db = get_database()
        document_repository = DocumentRepository(db)
        legal_section_repository = LegalSectionRepository(db)
        section_indexing_service = SectionIndexingService(
            legal_section_repository=legal_section_repository,
            semantic_index_dir="/app/pipeline/retrieval/semantic/search_index",
        )

        document = await document_repository.find_by_id(document_id)
        if not document:
            raise SystemExit(f"Document not found: {document_id}")

        source_path = Path(file_path)
        if not source_path.exists():
            raise SystemExit(f"Source file not found: {source_path}")

        extractor = GoogleCloudDocumentExtractor(
            credential_file=settings.google_application_credentials,
            bucket_name=settings.google_cloud_storage_bucket,
        )
        text = await extractor.extract_text([str(source_path)])
        if not text.strip():
            raise SystemExit("No text extracted from source file")

        section_count = await section_indexing_service.rebuild_document_sections_from_text(
            document_id=document_id,
            text=text,
            metadata=document,
        )
        indexed_documents = await section_indexing_service.rebuild_semantic_index()

        await document_repository.update_from_dict(document_id, {
            "indexed_sections": section_count,
            "semantic_index_documents": indexed_documents,
        })

        print(
            f"Backfilled document {document_id}: "
            f"sections={section_count}, indexed_documents={indexed_documents}"
        )
        return 0
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill legal sections and semantic index for an existing document.")
    parser.add_argument("--document-id", required=True)
    parser.add_argument("--file", required=True, help="Path to the original PDF/DOC/DOCX file.")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(main(args.document_id, args.file)))
