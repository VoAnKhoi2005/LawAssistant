import asyncio
from pathlib import Path
from typing import Any

import phonlp
from bson import ObjectId
from pymongo import MongoClient

from core.config import settings
from core.exceptions import BadRequestException, InternalServerException
from dto.retrieval_dto import RetrievalSearchRequest, RetrievalSearchResponse
from knowledge_graph.triplet_extraction.pos_taging.my_vncorenlp import init_vncorenlp


class RetrievalService:
    def __init__(self):
        self._pipeline = None
        self._mongo_client: MongoClient | None = None
        self._init_lock = asyncio.Lock()
        self._base_dir = Path(__file__).resolve().parents[1]
        self._retrieval_dir = self._base_dir / "pipeline" / "retrieval"
        self._dictionary_path = self._retrieval_dir / "preprocess_query" / "dictionary.json"
        self._semantic_index_dir = self._retrieval_dir / "semantic" / "search_index"

    async def search(self, request: RetrievalSearchRequest) -> RetrievalSearchResponse:
        query = request.query.strip()
        if not query:
            raise BadRequestException("Query must not be empty")

        pipeline = await self._get_pipeline(request)
        results = await asyncio.to_thread(pipeline.retrieve, query, request.top_k)

        return RetrievalSearchResponse(
            query=query,
            top_k=request.top_k,
            semantic_index_available=self._semantic_index_dir.exists(),
            results=[self._serialize_value(result) for result in results],
        )

    async def close(self):
        if self._mongo_client is not None:
            self._mongo_client.close()
            self._mongo_client = None

    async def _get_pipeline(self, request: RetrievalSearchRequest):
        semantic_enabled = self._semantic_enabled(request)
        needs_rebuild = (
            self._pipeline is None
            or self._pipeline.use_query_preprocessing != request.use_query_preprocessing
            or self._pipeline.use_graph_retrieval != request.use_graph_retrieval
            or self._pipeline.use_semantic_retrieval != semantic_enabled
            or self._pipeline.use_dpr != request.use_dpr
            or self._pipeline.k_hops != request.k_hops
        )
        if not needs_rebuild:
            return self._pipeline

        async with self._init_lock:
            semantic_enabled = self._semantic_enabled(request)
            needs_rebuild = (
                self._pipeline is None
                or self._pipeline.use_query_preprocessing != request.use_query_preprocessing
                or self._pipeline.use_graph_retrieval != request.use_graph_retrieval
                or self._pipeline.use_semantic_retrieval != semantic_enabled
                or self._pipeline.use_dpr != request.use_dpr
                or self._pipeline.k_hops != request.k_hops
            )
            if not needs_rebuild:
                return self._pipeline

            self._pipeline = await asyncio.to_thread(
                self._build_pipeline,
                request,
                semantic_enabled,
            )
            return self._pipeline

    def _build_pipeline(self, request: RetrievalSearchRequest, semantic_enabled: bool):
        try:
            from pipeline.retrieval.retrieval_pipeline import RetrievalPipeline
        except ImportError as exc:
            raise InternalServerException(
                message=f"Retrieval dependencies are not available: {exc}"
            ) from exc

        if self._mongo_client is None:
            self._mongo_client = MongoClient(settings.mongo_uri)

        vncorenlp_client = init_vncorenlp(settings.vncorenlp_model_path)
        phonlp_model = phonlp.load(save_dir=settings.phonlp_model_path)

        return RetrievalPipeline(
            openai_api_key=settings.openai_api_key,
            openai_model=settings.openai_model,
            dictionary_path=str(self._dictionary_path),
            mongo_client=self._mongo_client,
            db_name=settings.db_name,
            vncorenlp_client=vncorenlp_client,
            phonlp_model=phonlp_model,
            semantic_index_dir=str(self._semantic_index_dir),
            use_query_preprocessing=request.use_query_preprocessing,
            use_graph_retrieval=request.use_graph_retrieval,
            use_semantic_retrieval=semantic_enabled,
            use_dpr=request.use_dpr,
            k_hops=request.k_hops,
        )

    def _semantic_enabled(self, request: RetrievalSearchRequest) -> bool:
        return request.use_semantic_retrieval and self._semantic_index_dir.exists()

    def _serialize_value(self, value: Any):
        if isinstance(value, ObjectId):
            return str(value)
        if isinstance(value, dict):
            return {str(key): self._serialize_value(val) for key, val in value.items()}
        if isinstance(value, list):
            return [self._serialize_value(item) for item in value]
        return value
