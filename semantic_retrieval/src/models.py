"""Data models"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class Document:
    """Document model"""
    doc_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "content": self.content,
            **self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], id_field: str = "_id", content_field: str = "full_content") -> "Document":
        doc_id = str(data.get(id_field, ""))
        content = data.get(content_field, "")

        metadata = {k: v for k, v in data.items() if k not in [id_field, content_field]}
        metadata[id_field] = doc_id

        return cls(doc_id=doc_id, content=content, metadata=metadata)


@dataclass
class SearchResult:
    """Search result model"""
    doc_id: str
    content: str
    metadata: Dict[str, Any]
    rank: int
    score_combined: float
    score_semantic: float
    score_bm25: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "content": self.content,
            **self.metadata,
            "_rank": self.rank,
            "_scores": {
                "combined": round(self.score_combined, 4),
                "semantic": round(self.score_semantic, 4),
                "bm25": round(self.score_bm25, 4)
            }
        }


@dataclass
class IndexStats:
    """Index statistics"""
    total_documents: int
    faiss_vectors: int
    embedding_dim: int
    index_size_mb: float
    is_loaded: bool