from pydantic import BaseModel, Field


class RetrievalSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(20, ge=1, le=100)
    use_query_preprocessing: bool = True
    use_graph_retrieval: bool = True
    use_semantic_retrieval: bool = True
    use_dpr: bool = True
    k_hops: int = Field(2, ge=1, le=5)


class RetrievalSearchResponse(BaseModel):
    query: str
    top_k: int
    semantic_index_available: bool
    results: list[dict]
