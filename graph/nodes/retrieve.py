from typing import Any, Dict

from config.logger import logger
from graph.state import GraphState
from ingestion import retriever


def retrieve(state: GraphState) -> Dict[str, Any]:
    question = state["question"]
    logger.info("Retrieving documents", extra={"question": question})

    documents = retriever.invoke(question)
    logger.info("Retrieved documents", extra={"num_documents": len(documents)})
    return {"documents": documents, "question": question}
