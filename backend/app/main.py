from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field, conint, constr

from .rag import OpenSearchRetrieverStub, BedrockLLMClientStub, compose_citations

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


# Instantiate stubs once per process. In production these would be real clients.
_RETRIEVER = OpenSearchRetrieverStub()
_LLM = BedrockLLMClientStub()


@app.post("/rag/answer", response_model=RagResponse)
async def rag_answer(q: Question) -> RagResponse:
    """Return a retrieval-augmented answer using in-process stubs for OpenSearch & Bedrock.

    Steps implemented in this scaffold:
    1. Embed query and run KNN search (OpenSearchRetrieverStub.knn_search)
    2. Re-rank candidates by recency + section score + similarity
    3. Compose a context prompt made of source blocks
    4. Call BedrockLLMClientStub.generate_answer to synthesize an answer + confidence
    5. Return JSON with answer, citations, and metadata including confidence
    """
    # 1. Retrieve candidates
    candidates = _RETRIEVER.knn_search(q.query, top_k=q.top_k, course_id=q.course_id)

    # 2. Re-rank
    reranked = _RETRIEVER.rerank_by_recency_and_section(candidates)

    # 3. Compose context prompt (we pass docs directly to the LLM stub)
    context_docs = reranked

    # 4. Call LLM stub
    answer_text, confidence = _LLM.generate_answer(q.query, context_docs)

    # 5. Build citations list and metadata
    citations = compose_citations(context_docs)

    metadata: Dict[str, Any] = {"top_k": q.top_k, "course_id": q.course_id, "confidence": confidence}

    return RagResponse(answer=answer_text, citations=citations, metadata=metadata)
