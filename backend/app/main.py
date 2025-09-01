from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field, conint, constr

app = FastAPI(title="RAGEdu API")


class HealthResponse(BaseModel):
    status: str


class Question(BaseModel):
    query: constr(min_length=1) = Field(..., description="User question")
    course_id: Optional[str] = Field(None, description="Optional course id to scope retrievals")
    top_k: conint(ge=1) = Field(5, description="Number of results to retrieve; must be >= 1")


class RagResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health endpoint used by monitors and CI."""
    return HealthResponse(status="ok")


@app.post("/rag/answer", response_model=RagResponse)
async def rag_answer(q: Question) -> RagResponse:
    """Return a stubbed RAG answer. This will be wired up to retrieval + LLM later.

    The request model validates the inputs (query non-empty, top_k >= 1).
    """
    # TODO: wire OpenSearch retrieval + Bedrock/LLM
    return RagResponse(
        answer="This is a stub. Retrieval and LLM will be wired in subsequent PRs.",
        citations=[],
        metadata={"top_k": q.top_k, "course_id": q.course_id},
    )
