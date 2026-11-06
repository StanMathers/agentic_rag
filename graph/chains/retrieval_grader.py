from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen3:1.7b")


class GradeDocuments(BaseModel):
    """
    Binary score for relevance check on retrieved documents
    """

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


structured_llm_grader = llm.with_structured_output(GradeDocuments)


system = """
    You are a grader assesing the relevance of retrieved documents to a given question.
    If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant, otherwise grade it as not relevant.
    Give a binary score of 'yes' or 'no' score to indicate whether the document is relevant to the question or not.
"""

grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("user", "Retrieved document: \n\n {document} \n\n User question: {question}"),
    ]
)

retrieval_grader = grade_prompt | structured_llm_grader
