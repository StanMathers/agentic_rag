from fastapi import FastAPI
from backend.routes.health import router as health_router
from backend.routes.ingestion import router as ingestion_router
from backend.routes.query import router as query_router
from backend.middleware import LoggingMiddleware

app = FastAPI()

app.add_middleware(LoggingMiddleware)

app.include_router(health_router, prefix="/v1", tags=["health"])
app.include_router(query_router, prefix="/v1/query", tags=["query"])
app.include_router(ingestion_router, prefix="/v1/ingestion", tags=["ingestion"])
