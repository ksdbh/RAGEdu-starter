from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="RAGEdu API")


class Question(BaseModel):
    """Incoming question payload for the RAG endpoint."""

    query: str = Field(..., min_length=1)
    course_id: Optional[str] = None
    top_k: int = Field(5, ge=1, description="How many documents to retrieve; must be >= 1")


class RAGAnswer(BaseModel):
    """Response model for the RAG endpoint."""

    answer: str
    citations: List[Any]
    metadata: Dict[str, Any]


@app.get("/health")
def health() -> Dict[str, str]:
    """Simple liveness/health endpoint."""
    return {"status": "ok"}


@app.post("/rag/answer", response_model=RAGAnswer)
def rag_answer(question: Question):
    """Stub RAG endpoint.

    This is intentionally simple for now and returns a deterministic placeholder
    so callers and tests can rely on a stable contract. Retrieval + LLM wiring
    will be added in later changes.
    """
    # TODO: wire OpenSearch retrieval + Bedrock / other LLM
    return {
        "answer": "This is a stub. Retrieval and LLM will be wired in subsequent PRs.",
        "citations": [],
        "metadata": {"top_k": question.top_k, "course_id": question.course_id},
    }
