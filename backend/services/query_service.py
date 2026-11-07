from graph.graph import app
from backend.schemas.query import QueryRequest, QueryResponse


def invoke_graph(query_request: QueryRequest) -> QueryResponse:
    result = app.invoke(input={"question": query_request.query})
    return QueryResponse(response=result["generation"])
