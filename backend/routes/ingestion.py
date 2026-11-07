from fastapi import APIRouter, Depends

from backend.dependencies import get_ingestion_service
from backend.schemas.ingestion import DocumentIngestionRequest, DocumentIngestionResponse
from backend.services.ingestion_service import IngestionService

router = APIRouter()


@router.post("/ingest")
def ingest(
    request: DocumentIngestionRequest,
    service: IngestionService = Depends(get_ingestion_service),
) -> DocumentIngestionResponse:
    result = service.ingest(request.urls)
    return DocumentIngestionResponse(
        num_documents=result.num_documents, num_chunks=result.num_chunks
    )
