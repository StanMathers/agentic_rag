from fastapi import APIRouter, Request
from backend.schemas.query import QueryRequest, QueryResponse
from backend.services.query_service import invoke_graph

router = APIRouter()


@router.post("/query")
async def query(request: Request, query_request: QueryRequest) -> QueryResponse:
    return invoke_graph(query_request)
