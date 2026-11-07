from dataclasses import dataclass
from typing import Protocol, Sequence

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore, VectorStoreRetriever
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter, TextSplitter

from config.logger import logger
from config.settings import IngestionSettings

_PRIMITIVE_METADATA = (str, int, float, bool)


@dataclass(frozen=True)
class IngestionResult:
    num_documents: int
    num_chunks: int


class DocumentLoader(Protocol):
    def load(self, sources: Sequence[str]) -> list[Document]: ...


class UnstructuredWebLoader:
    def __init__(
        self, chunking_strategy: str = "basic", max_characters: int = 1_000_000
    ):
        self.chunking_strategy = chunking_strategy
        self.max_characters = max_characters

    def load(self, sources: Sequence[str]) -> list[Document]:
        from langchain_unstructured import UnstructuredLoader

        documents: list[Document] = []
        for url in sources:
            loader = UnstructuredLoader(
                web_url=url,
                chunking_strategy=self.chunking_strategy,
                max_characters=self.max_characters,
            )
            documents.extend(loader.load())
        return documents


def _filter_complex_metadata(documents: list[Document]) -> list[Document]:
    return [
        Document(
            page_content=doc.page_content,
            metadata={
                k: v
                for k, v in doc.metadata.items()
                if isinstance(v, _PRIMITIVE_METADATA)
            },
        )
        for doc in documents
    ]


class IngestionService:
    def __init__(
        self,
        loader: DocumentLoader,
        splitter: TextSplitter,
        vector_store: VectorStore,
    ):
        self.loader = loader
        self.splitter = splitter
        self.vector_store = vector_store

    def ingest(self, sources: Sequence[str]) -> IngestionResult:
        logger.info("Loading documents", extra={"num_sources": len(sources)})
        documents = self.loader.load(sources)

        chunks = self.splitter.split_documents(documents)
        chunks = _filter_complex_metadata(chunks)
        logger.info(
            "Split documents",
            extra={"num_documents": len(documents), "num_chunks": len(chunks)},
        )

        if chunks:
            self.vector_store.add_documents(chunks)
        logger.info("Stored chunks", extra={"num_chunks": len(chunks)})

        return IngestionResult(num_documents=len(documents), num_chunks=len(chunks))

    def as_retriever(self, **kwargs) -> VectorStoreRetriever:
        return self.vector_store.as_retriever(**kwargs)


def build_loader(settings: IngestionSettings) -> DocumentLoader:
    return UnstructuredWebLoader()


def build_splitter(settings: IngestionSettings) -> TextSplitter:
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
    )


def build_embeddings(settings: IngestionSettings) -> Embeddings:
    return OllamaEmbeddings(model=settings.embedding_model)


def build_vector_store(
    settings: IngestionSettings, embeddings: Embeddings
) -> VectorStore:
    if settings.chroma_host:
        return Chroma(
            collection_name=settings.collection_name,
            embedding_function=embeddings,
            host=settings.chroma_host,
            port=settings.chroma_port,
        )
    return Chroma(
        collection_name=settings.collection_name,
        embedding_function=embeddings,
        persist_directory=settings.persist_directory,
    )


def build_ingestion_service(
    settings: IngestionSettings | None = None,
    *,
    loader: DocumentLoader | None = None,
    splitter: TextSplitter | None = None,
    embeddings: Embeddings | None = None,
    vector_store: VectorStore | None = None,
) -> IngestionService:
    """Wire the ingestion pipeline. Any part passed in replaces the default;
    everything else is built from settings."""
    settings = settings or IngestionSettings()

    if vector_store is None:
        vector_store = build_vector_store(
            settings, embeddings or build_embeddings(settings)
        )

    return IngestionService(
        loader=loader or build_loader(settings),
        splitter=splitter or build_splitter(settings),
        vector_store=vector_store,
    )
