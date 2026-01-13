from dataclasses import dataclass, field
from typing import List


@dataclass
class SearchConfig:
    """Main configuration"""

    # Index storage
    index_dir: str = "./search_index"

    # Embedding
    embedding_model: str = "bkai-foundation-models/vietnamese-bi-encoder"
    embedding_batch_size: int = 256  # Batch size khi encode

    # Processing
    processing_batch_size: int = 1000  # Batch size khi load từ DB

    # Search defaults
    default_top_k: int = 10
    default_semantic_weight: float = 0.6
    default_bm25_weight: float = 0.4

    # Fields
    content_field: str = "full_content"
    id_field: str = "_id"

    cached_fields: List[str] = field(default_factory=lambda: [
        "_id", "id", "full_content", "full_path",
        "document_title", "so_hieu", "effective_date",
        "leaf_type", "parents_chain"
    ])