from typing import Any, Dict

from graph.chains.retrieval_grader import GradeDocuments, retrieval_grader
from graph.state import GraphState


def grade_documents(state: GraphState) -> Dict[str, Any]:
    """
    Determines whether the retrieved documents are relevant to the question
    If any document is not relevant, we will set a flag to run web search

    Args:
        state (dict): The current graph state
    Returns:
        state (dict): Filtered out irrelevant documents and updated web_search
    """

    question = state["question"]
    documents = state["documents"]

    filtered_documents = []
    web_search = False

    for doc in documents:
        score: GradeDocuments = retrieval_grader.invoke(
            {"question": question, "document": doc.page_content}
        )

        if score.binary_score.lower() == "yes":
            print("Document relevant")
            filtered_documents.append(doc)
        else:
            print("Document not relevant")
            web_search = True
            continue

    return {
        "documents": filtered_documents,
        "question": question,
        "web_search": web_search,
    }
