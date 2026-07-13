from fastapi import APIRouter, Depends, Request

from core.security import get_current_user
from dto.retrieval_dto import RetrievalSearchRequest
from utils.api_response_helper import success_response


def create_retrieval_router_with_state() -> APIRouter:
    router = APIRouter(
        prefix="/api/retrieval",
        tags=["retrieval"],
        dependencies=[Depends(get_current_user)],
    )

    @router.post("/search")
    async def search_retrieval(
        request: RetrievalSearchRequest,
        req: Request,
    ):
        data = await req.app.state.retrieval_controller.search(request)
        return success_response(data, message="Retrieval completed successfully")

    return router
