import logging
from typing import List, Dict, Any, Optional, Tuple
from core.interfaces.document_extractor_interface import IDocumentExtractor
from core.interfaces.text_simplifier_interface import ITextSimplifier
from core.interfaces.triplet_extractor_interface import ITripletExtractor
from repositories.document_repository import DocumentRepository
from repositories.triplet_repository import TripletRepository
from repositories.concept_repository import ConceptRepository
from repositories.relation_repository import RelationRepository
from repositories.upload_file_repository import UploadFileRepository
from services.section_indexing_service import SectionIndexingService
from models.triplet_model import Triplet
from models.concept_model import Concept
from models.relation_model import Relation
from models.common import DocumentRef


logger = logging.getLogger(__name__)


class DocumentProcessor:
    TRIPLET_SAVE_BATCH_SIZE = 10

    def __init__(
        self,
        document_repository: DocumentRepository,
        triplet_repository: TripletRepository,
        concept_repository: ConceptRepository,
        relation_repository: RelationRepository,
        section_indexing_service: SectionIndexingService,
        upload_file_repository: Optional[UploadFileRepository],
        document_extractor: IDocumentExtractor,
        text_simplifier: ITextSimplifier,
        triplet_extractor: ITripletExtractor
    ):
        self.document_repository = document_repository
        self.triplet_repository = triplet_repository
        self.concept_repository = concept_repository
        self.relation_repository = relation_repository
        self.section_indexing_service = section_indexing_service
        self.upload_file_repository = upload_file_repository
        
        # Infrastructure dependencies injected
        self.document_extractor = document_extractor
        self.text_simplifier = text_simplifier
        self.triplet_extractor = triplet_extractor

    async def process_document_pipeline(
        self,
        document_id: str,
        file_paths: List[str],
        metadata: Dict[str, Any],
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Process document through 3-step pipeline:
        1. Extract text from document
        2. Parse and save legal sections
        3. Rebuild semantic retrieval index
        4. Simplify legal sentences
        5. Extract knowledge triplets
        """
        def update(step: str, progress: int):
            if progress_callback:
                progress_callback(step, progress)

        try:
            existing_document = await self.document_repository.find_by_id(document_id)

            # Step 1: Extract text from document
            await self.document_repository.update_from_dict(
                document_id, {"status": "extracting_text"}
            )
            update("Extracting text from document", 10)
            text = await self._extract_text(file_paths)

            # Step 2: Parse legal sections and save them for retrieval.
            await self.document_repository.update_from_dict(
                document_id, {"status": "building_sections"}
            )
            update("Building legal sections", 25)
            section_count = await self.section_indexing_service.rebuild_document_sections_from_text(
                document_id=document_id,
                text=text,
                metadata=metadata,
            )

            # Step 3: Rebuild semantic retrieval index after section changes.
            await self.document_repository.update_from_dict(
                document_id, {"status": "building_index", "indexed_sections": section_count}
            )
            update("Rebuilding retrieval index", 35)
            indexed_documents = await self.section_indexing_service.rebuild_semantic_index()

            # Step 4: Simplify legal sentences
            await self.document_repository.update_from_dict(
                document_id, {"status": "simplifying"}
            )
            update("Simplifying legal sentences", 40)
            simplified_sentences = await self._simplify_text(text)
            
            await self.document_repository.update_from_dict(
                document_id, {
                    "status": "extracting_triplets",
                    "processed_sentences": len(simplified_sentences),
                    "triplet_sentences_total": len(simplified_sentences),
                }
            )

            # Step 5: Extract knowledge triplets
            update("Extracting knowledge triplets", 80)
            saved_triplets = await self._extract_and_save_triplets(
                document_id=document_id,
                sentences=simplified_sentences,
                metadata=metadata,
                existing_document=existing_document,
                progress_callback=update,
            )

            # Update document status to completed
            await self.document_repository.update_from_dict(
                document_id, {
                    "status": "completed",
                    "indexed_sections": section_count,
                    "semantic_index_documents": indexed_documents,
                    "processed_sentences": len(simplified_sentences),
                    "triplet_sentences_processed": len(simplified_sentences),
                    "extracted_triplets": len(saved_triplets),
                }
            )
            await self._update_file_statuses(metadata, "done")

            update("Processing completed", 100)

            return {
                "document_id": document_id,
                "indexed_sections": section_count,
                "semantic_index_documents": indexed_documents,
                "processed_sentences": len(simplified_sentences),
                "extracted_triplets": len(saved_triplets),
                "status": "completed"
            }

        except Exception as e:
            # Update document status to failed
            await self.document_repository.update_from_dict(
                document_id, {
                    "status": "failed",
                    "error": str(e)
                }
            )
            await self._update_file_statuses(metadata, "failed", str(e))
            raise

    async def _extract_text(self, file_paths: List[str]) -> str:
        """
        Step 1: Extract text from document files
        Delegates to injected document extractor implementation
        """
        return await self.document_extractor.extract_text(file_paths)

    async def _simplify_text(self, text: str) -> List[str]:
        """
        Step 2: Simplify legal sentences
        Delegates to injected text simplifier implementation
        """
        return await self.text_simplifier.simplify_text(text)

    async def _extract_triplets(self, sentences: List[str]) -> List[Tuple[str, str, str]]:
        """
        Step 3: Extract knowledge triplets (subject, relation, object)
        Delegates to injected triplet extractor implementation
        """
        return await self.triplet_extractor.extract_triplets(sentences)

    async def _extract_and_save_triplets(
        self,
        document_id: str,
        sentences: List[str],
        metadata: Dict[str, Any],
        existing_document: Optional[Dict[str, Any]],
        progress_callback=None,
    ) -> List[str]:
        saved_triplet_ids: List[str] = []
        already_processed = self._get_resume_sentence_offset(existing_document, len(sentences))

        if already_processed >= len(sentences):
            await self.document_repository.update_from_dict(
                document_id,
                {
                    "triplet_sentences_processed": len(sentences),
                    "extracted_triplets": existing_document.get("extracted_triplets", 0)
                    if existing_document
                    else 0,
                },
            )
            return await self._load_saved_triplet_ids(document_id)

        if already_processed > 0:
            await self.document_repository.update_from_dict(
                document_id,
                {
                    "resume_from_sentence": already_processed,
                    "status": "extracting_triplets",
                },
            )

        pending_triplets: List[Tuple[str, str, str]] = []

        for sentence_index in range(already_processed, len(sentences)):
            sentence = sentences[sentence_index]
            sentence_triplets = await self._extract_triplets([sentence])
            pending_triplets.extend(sentence_triplets)

            should_flush = (
                len(pending_triplets) >= self.TRIPLET_SAVE_BATCH_SIZE
                or sentence_index == len(sentences) - 1
            )
            if not should_flush:
                continue

            flushed_ids = await self._save_triplets_to_db(
                document_id=document_id,
                triplet_data=pending_triplets,
                metadata=metadata,
            )
            saved_triplet_ids.extend(flushed_ids)
            pending_triplets = []

            processed_count = sentence_index + 1
            extracted_count = await self.triplet_repository.count_by_document(document_id)
            await self.document_repository.update_from_dict(
                document_id,
                {
                    "status": "extracting_triplets",
                    "triplet_sentences_processed": processed_count,
                    "extracted_triplets": extracted_count,
                },
            )

            logger.info(
                "[CHECKPOINT] Document %s saved batch: sentences=%s/%s, total_triplets=%s",
                document_id,
                processed_count,
                len(sentences),
                extracted_count,
            )

            if progress_callback:
                progress = 80 + int((processed_count / max(len(sentences), 1)) * 19)
                progress_callback("Extracting knowledge triplets", min(progress, 99))

        return await self._load_saved_triplet_ids(document_id)

    async def _save_triplets_to_db(
        self,
        document_id: str,
        triplet_data: List[Tuple[str, str, str]],
        metadata: Dict[str, Any]
    ) -> List[str]:
        """Save extracted triplets to database with concept/relation management"""
        saved_triplet_ids = []
        
        so_hieu = metadata.get("so_hieu", "")
        document_ref = DocumentRef(section_id=document_id, so_hieu=so_hieu)
        
        for subject_name, relation_name, object_name in triplet_data:
            subject_name = self._normalize_graph_value(subject_name)
            relation_name = self._normalize_graph_value(relation_name)
            object_name = self._normalize_graph_value(object_name)

            if not subject_name or not relation_name or not object_name:
                continue

            # Get or create subject concept
            subject_id = await self._get_or_create_concept(subject_name, document_ref)
            
            # Get or create relation
            relation_id = await self._get_or_create_relation(relation_name, document_ref)
            
            # Get or create object concept
            object_id = await self._get_or_create_concept(object_name, document_ref)
            
            # Create triplet
            triplet = Triplet(
                subject_id=subject_id,
                subject_name=subject_name,
                relation_id=relation_id,
                relation_name=relation_name,
                object_id=object_id,
                object_name=object_name,
                documents=[document_ref]
            )
            
            created_triplet = await self.triplet_repository.upsert_graph_triplet(
                triplet,
                document_ref,
            )
            saved_triplet_ids.append(created_triplet.id)
        
        return saved_triplet_ids

    async def _load_saved_triplet_ids(self, document_id: str) -> List[str]:
        triplet_dicts = await self.triplet_repository.find_by_document(document_id, skip=0, limit=100000)
        return [str(triplet["_id"]) for triplet in triplet_dicts]

    async def _get_or_create_concept(self, concept_name: str, document_ref: DocumentRef) -> str:
        """Get existing concept or create new one"""
        return await self.concept_repository.find_or_create_with_document(concept_name, document_ref)

    async def _get_or_create_relation(self, relation_name: str, document_ref: DocumentRef) -> Optional[str]:
        """Get existing relation or create new one"""
        return await self.relation_repository.find_or_create_with_document(
            relation_name,
            document_ref,
        )

    async def _update_file_statuses(self, metadata: Dict[str, Any], status: str, error: Optional[str] = None) -> None:
        if not self.upload_file_repository:
            return

        for file_ref in metadata.get("files", []):
            file_id = file_ref.get("file_id") if isinstance(file_ref, dict) else None
            if file_id:
                await self.upload_file_repository.update_status(file_id, status, error)

    @staticmethod
    def _normalize_graph_value(value: Optional[str]) -> str:
        if value is None:
            return ""
        return " ".join(str(value).split())

    @staticmethod
    def _get_resume_sentence_offset(existing_document: Optional[Dict[str, Any]], total_sentences: int) -> int:
        if not existing_document:
            return 0

        processed = existing_document.get("triplet_sentences_processed", 0) or 0
        if not isinstance(processed, int):
            return 0
        if processed < 0:
            return 0
        return min(processed, total_sentences)
