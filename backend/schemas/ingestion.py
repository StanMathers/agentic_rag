from typing import List
from pydantic import BaseModel, Field


class DocumentIngestionRequest(BaseModel):
    urls: List[str] = Field(
        default=[
            "https://lilianweng.github.io/posts/2023-06-23-agent/",
            "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
            "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
        ],
        description="A list of URLs to ingest documents from.",
    )


class DocumentIngestionResponse(BaseModel):
    num_documents: int = Field(..., description="Number of documents loaded.")
    num_chunks: int = Field(..., description="Number of chunks stored.")
