from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from knowledge_graph.triplet_extraction.doc_extraction.parse_text_to_section import parse_document
from knowledge_graph.triplet_extraction.doc_extraction.utils import clean_title, strip_markdown_formatting
from pipeline.retrieval.semantic.config import SearchConfig
from pipeline.retrieval.semantic.hybrid_search import HybridSearchEngine
from repositories.legal_section_repository import LegalSectionRepository


logger = logging.getLogger(__name__)


class SectionIndexingService:
    def __init__(self, legal_section_repository: LegalSectionRepository, semantic_index_dir: str):
        self.legal_section_repository = legal_section_repository
        self.semantic_index_dir = Path(semantic_index_dir)

    async def rebuild_document_sections_from_text(
        self,
        *,
        document_id: str,
        text: str,
        metadata: dict[str, Any],
    ) -> int:
        so_hieu = metadata["so_hieu"]
        title = clean_title(metadata.get("title", so_hieu))
        effective_date = self._normalize_effective_date(metadata.get("effective_date"))
        source_files = metadata.get("source_files") or metadata.get("files") or []
        source_file_names = ", ".join(
            file_ref.get("filename", "")
            for file_ref in source_files
            if isinstance(file_ref, dict) and file_ref.get("filename")
        )

        cleaned_text = strip_markdown_formatting(text)
        parsed_sections = parse_document(cleaned_text, so_hieu)
        if not parsed_sections:
            raise ValueError(f"No legal sections were parsed for document {so_hieu}")

        await self.legal_section_repository.delete_by_so_hieu(so_hieu)

        for section_id, section_data in parsed_sections.items():
            section_record = {
                **section_data,
                "_id": section_id,
                "document_id": document_id,
                "document_title": title,
                "effective_date": effective_date,
                "source_file": source_file_names,
            }
            await self.legal_section_repository.upsert_from_dict(section_id, section_record)

        logger.info("Saved %s legal sections for %s", len(parsed_sections), so_hieu)
        return len(parsed_sections)

    async def rebuild_semantic_index(self, so_hieu: Optional[str] = None) -> int:
        documents = await self._build_semantic_documents(so_hieu=so_hieu)
        await asyncio.to_thread(self._rebuild_semantic_index_sync, documents)
        return len(documents)

    async def _build_semantic_documents(self, so_hieu: Optional[str] = None) -> list[dict[str, Any]]:
        if so_hieu:
            sections = await self.legal_section_repository.find_all_by_so_hieu(so_hieu)
        else:
            sections = await self.legal_section_repository.find_all(skip=0, limit=100000)

        if not sections:
            return []

        section_map = {str(section["_id"]): section for section in sections}
        parent_ids = {
            str(section["parent_id"])
            for section in sections
            if section.get("parent_id")
        }

        semantic_documents: list[dict[str, Any]] = []
        for section in sections:
            section_id = str(section["_id"])
            if section_id in parent_ids:
                continue
            if section.get("is_amendment"):
                continue

            chain = self._build_chain(section, section_map)
            content_parts = []
            for node in chain:
                if node.get("content"):
                    content_parts.append(str(node["content"]).strip())

            full_content = "\n".join(part for part in content_parts if part).strip()
            if not full_content:
                continue

            semantic_documents.append({
                "_id": section_id,
                "id": section_id,
                "full_content": full_content,
                "full_path": section.get("full_path", ""),
                "document_title": section.get("document_title", ""),
                "so_hieu": section.get("so_hieu", ""),
                "effective_date": section.get("effective_date", ""),
                "leaf_type": section.get("type", ""),
                "parents_chain": [
                    {
                        "id": str(node["_id"]),
                        "title": node.get("title", ""),
                        "type": node.get("type", ""),
                    }
                    for node in chain
                ],
            })

        return semantic_documents

    def _rebuild_semantic_index_sync(self, documents: list[dict[str, Any]]) -> None:
        engine = HybridSearchEngine(SearchConfig(index_dir=str(self.semantic_index_dir)))
        if not documents:
            logger.warning("No semantic documents available to index")
            return

        engine.rebuild_index(documents)
        logger.info("Rebuilt semantic index with %s documents", len(documents))

    @staticmethod
    def _build_chain(section: dict[str, Any], section_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        chain = []
        current = section
        while current:
            chain.append(current)
            parent_id = current.get("parent_id")
            current = section_map.get(str(parent_id)) if parent_id else None
        chain.reverse()
        return chain

    @staticmethod
    def _normalize_effective_date(value: Any) -> str:
        if isinstance(value, dict) and "date" in value:
            value = value["date"]
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, str):
            return value
        return ""
