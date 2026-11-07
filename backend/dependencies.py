from functools import lru_cache

from backend.services.ingestion_service import IngestionService, build_ingestion_service


@lru_cache
def get_ingestion_service() -> IngestionService:
    return build_ingestion_service()
