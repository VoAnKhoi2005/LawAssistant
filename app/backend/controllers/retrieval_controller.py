from dto.retrieval_dto import RetrievalSearchRequest
from services.retrieval_service import RetrievalService


class RetrievalController:
    def __init__(self, retrieval_service: RetrievalService):
        self.retrieval_service = retrieval_service

    async def search(self, request: RetrievalSearchRequest):
        return await self.retrieval_service.search(request)
