from typing import List, Dict, Any, Optional, Tuple
from core.interfaces.document_extractor_interface import IDocumentExtractor
from core.interfaces.text_simplifier_interface import ITextSimplifier
from core.interfaces.triplet_extractor_interface import ITripletExtractor
from repositories.document_repository import DocumentRepository
from repositories.triplet_repository import TripletRepository
from repositories.concept_repository import ConceptRepository
from repositories.relation_repository import RelationRepository
from models.triplet_model import Triplet
from models.concept_model import Concept
from models.relation_model import Relation
from models.common import DocumentRef


class DocumentProcessor:
    def __init__(
        self,
        document_repository: DocumentRepository,
        triplet_repository: TripletRepository,
        concept_repository: ConceptRepository,
        relation_repository: RelationRepository,
        document_extractor: IDocumentExtractor,
        text_simplifier: ITextSimplifier,
        triplet_extractor: ITripletExtractor
    ):
        self.document_repository = document_repository
        self.triplet_repository = triplet_repository
        self.concept_repository = concept_repository
        self.relation_repository = relation_repository
        
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
        2. Simplify legal sentences
        3. Extract knowledge triplets
        """
        def update(step: str, progress: int):
            if progress_callback:
                progress_callback(step, progress)

        try:
            # Update document status to processing
            await self.document_repository.update_from_dict(
                document_id, {"status": "processing"}
            )

            # Step 1: Extract text from document
            update("Extracting text from document", 10)
            text = await self._extract_text(file_paths)
            
            await self.document_repository.update_from_dict(
                document_id, {"status": "extracting_text"}
            )

            # Step 2: Simplify legal sentences
            update("Simplifying legal sentences", 40)
            simplified_sentences = await self._simplify_text(text)
            
            await self.document_repository.update_from_dict(
                document_id, {
                    "status": "simplifying",
                    "processed_sentences": len(simplified_sentences)
                }
            )

            # Step 3: Extract knowledge triplets
            update("Extracting knowledge triplets", 80)
            triplet_data = await self._extract_triplets(simplified_sentences)
            
            # Save triplets to database
            saved_triplets = await self._save_triplets_to_db(
                document_id, triplet_data, metadata
            )

            # Update document status to completed
            await self.document_repository.update_from_dict(
                document_id, {
                    "status": "completed",
                    "processed_sentences": len(simplified_sentences),
                    "extracted_triplets": len(saved_triplets)
                }
            )

            update("Processing completed", 100)

            return {
                "document_id": document_id,
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

    async def _save_triplets_to_db(
        self,
        document_id: str,
        triplet_data: List[Tuple[str, str, str]],
        metadata: Dict[str, Any]
    ) -> List[str]:
        """Save extracted triplets to database with concept/relation management"""
        saved_triplet_ids = []
        
        so_hieu = metadata.get("so_hieu", "")
        
        for subject_name, relation_name, object_name in triplet_data:
            # Get or create subject concept
            subject_id = await self._get_or_create_concept(subject_name)
            
            # Get or create relation
            relation_id = await self._get_or_create_relation(relation_name)
            
            # Get or create object concept
            object_id = await self._get_or_create_concept(object_name)
            
            # Create triplet
            triplet = Triplet(
                subject_id=subject_id,
                subject_name=subject_name,
                relation_id=relation_id,
                relation_name=relation_name,
                object_id=object_id,
                object_name=object_name,
                documents=[DocumentRef(section_id=document_id, so_hieu=so_hieu)]
            )
            
            created_triplet = await self.triplet_repository.create(triplet)
            saved_triplet_ids.append(created_triplet.id)
        
        return saved_triplet_ids

    async def _get_or_create_concept(self, concept_name: str) -> str:
        """Get existing concept or create new one"""
        existing_concept = await self.concept_repository.find_by_name(concept_name)
        
        if existing_concept:
            return str(existing_concept["_id"])
        
        new_concept = Concept(name=concept_name)
        created_concept = await self.concept_repository.create(new_concept)
        return created_concept.id

    async def _get_or_create_relation(self, relation_name: str) -> Optional[str]:
        """Get existing relation or create new one"""
        existing_relations = await self.relation_repository.find_by_relation_name(relation_name)
        
        if existing_relations and len(existing_relations) > 0:
            return str(existing_relations[0]["_id"])
        
        new_relation = Relation(relation_name=relation_name)
        created_relation = await self.relation_repository.create(new_relation)
        return created_relation.id