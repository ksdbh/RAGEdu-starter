from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, conint, constr

from .rag import OpenSearchRetrieverStub, BedrockLLMClientStub, compose_citations
from .db import DynamoDBRecorder

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


# New models for quiz generation / submission
class QuizGenerateRequest(BaseModel):
    query: constr(min_length=1) = Field(..., description="Seed query/topic for the quiz")
    course_id: Optional[str] = None
    num_questions: conint(ge=1, le=10) = 5


class QuizQuestionOut(BaseModel):
    id: str
    type: constr(regex="^(mcq|short)$")
    prompt: str
    choices: Optional[List[str]] = None
    answer: str
    distractors: List[str]
    spaced_rep: Dict[str, Any]


class QuizGenerateResponse(BaseModel):
    quiz_id: str
    questions: List[QuizQuestionOut]
    metadata: Dict[str, Any]


class QuizResultItem(BaseModel):
    question_id: str
    correct: bool
    response: Optional[str] = None
    time_ms: Optional[int] = None


class QuizSubmitRequest(BaseModel):
    quiz_id: str
    user_id: Optional[str] = None
    results: List[QuizResultItem]


class QuizSubmitResponse(BaseModel):
    success: bool
    recorded: int


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health endpoint used by monitors and CI."""
    return HealthResponse(status="ok")


# Instantiate stubs once per process. In production these would be real clients.
_RETRIEVER = OpenSearchRetrieverStub()
_LLM = BedrockLLMClientStub()
_DB = DynamoDBRecorder()  # best-effort recorder; will no-op if AWS not configured


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


@app.post("/quiz/generate", response_model=QuizGenerateResponse)
async def quiz_generate(payload: QuizGenerateRequest) -> QuizGenerateResponse:
    """Generate a short quiz (default 5 questions) grounded in retrieved chunks.

    This endpoint uses the retriever to get context documents for the provided query
    and synthesizes a small set of questions (mix of MCQ and short-answer).

    The returned questions include correct answers and distractors derived from the
    context (deterministic heuristics, safe for the scaffold).
    Each question also includes simple spaced-repetition metadata (ease and interval in days).
    """
    # Retrieve a larger set of candidates to draw distractors from
    candidates = _RETRIEVER.knn_search(payload.query, top_k=max(10, payload.num_questions * 2), course_id=payload.course_id)
    if not candidates:
        raise HTTPException(status_code=404, detail="No context documents found for quiz generation")

    # Rerank to prioritize best context
    context_docs = _RETRIEVER.rerank_by_recency_and_section(candidates)

    # Build questions deterministically from top docs
    questions = []
    import uuid

    # Helper to extract a short answer phrase from a doc (first sentence / 8-12 words)
    def extract_answer_from_text(text: str) -> str:
        s = text.strip().split(".\n")[0]
        # fallback to first sentence-like split
        import re

        parts = re.split(r"(?<=[.!?])\s+", text.strip())
        if parts:
            s = parts[0]
        words = s.split()
        if len(words) <= 12:
            return s.strip().rstrip('.')
        return " ".join(words[:10]).rstrip('.')

    # Collect candidate phrases for distractors
    candidate_phrases = []
    for d in context_docs:
        candidate_phrases.append(extract_answer_from_text(d.get("text", "")))

    # ensure uniqueness and filter empties
    candidate_phrases = [p for i, p in enumerate(candidate_phrases) if p and p not in candidate_phrases[:i]]

    for i in range(payload.num_questions):
        # pick a doc cycling through top results
        doc = context_docs[i % len(context_docs)]
        title = doc.get("title") or "Source"
        prompt_base = f"Based on {title} (page {doc.get('page')}):"
        text = doc.get("text", "")
        answer = extract_answer_from_text(text)

        # Build distractors by selecting other candidate_phrases of similar length
        distractors = []
        for p in candidate_phrases:
            if p == answer:
                continue
            # simple similarity: prefer phrases with similar word-count
            if abs(len(p.split()) - len(answer.split())) <= 3:
                distractors.append(p)
        # fallback: take any other phrases
        if len(distractors) < 3:
            distractors = [p for p in candidate_phrases if p != answer][:3]

        # Ensure unique distractors and limit to 3 for MCQ
        distractors = list(dict.fromkeys(distractors))[:3]

        # Decide type: alternate mcq and short for variety
        q_type = "mcq" if i % 2 == 0 else "short"

        q_id = uuid.uuid4().hex

        spaced = {"ease": 2.5, "interval_days": 1}

        if q_type == "mcq":
            # Assemble choices: correct + distractors, deterministic order (shuffle by index)
            choices = [answer] + distractors
            # Ensure at least 2 choices
            if len(choices) < 2:
                # fabricate a simple distractor by truncating/altering answer
                alt = (" ".join(answer.split()[: max(1, len(answer.split()) - 1)])).strip()
                if alt and alt != answer:
                    choices.append(alt)
                else:
                    choices.append(answer + " (see source)")
            # Deterministic pseudo-shuffle: rotate based on question index
            rot = i % len(choices)
            choices = choices[rot:] + choices[:rot]

            question = {
                "id": q_id,
                "type": "mcq",
                "prompt": f"{prompt_base} {answer.split('.')[0].strip()} - choose the best answer.",
                "choices": choices,
                "answer": answer,
                "distractors": [c for c in choices if c != answer],
                "spaced_rep": spaced,
            }
        else:
            question = {
                "id": q_id,
                "type": "short",
                "prompt": f"{prompt_base} Briefly answer: what is {answer.split()[0] if answer else 'this'}?",
                "choices": None,
                "answer": answer,
                "distractors": distractors,
                "spaced_rep": spaced,
            }
        questions.append(question)

    quiz_id = uuid.uuid4().hex
    metadata = {"num_questions": len(questions), "course_id": payload.course_id}
    return QuizGenerateResponse(quiz_id=quiz_id, questions=questions, metadata=metadata)


@app.post("/quiz/submit", response_model=QuizSubmitResponse)
async def quiz_submit(payload: QuizSubmitRequest) -> QuizSubmitResponse:
    """Record quiz results into DynamoDB (best-effort).

    The recorder will attempt to put items into a table; failures are handled gracefully
    so this endpoint is safe to call in local/dev environments without AWS creds.
    """
    if not payload.results:
        raise HTTPException(status_code=400, detail="No results provided")

    recorded = 0
    for r in payload.results:
        item = {
            "quiz_id": payload.quiz_id,
            "question_id": r.question_id,
            "user_id": payload.user_id,
            "correct": r.correct,
            "response": r.response,
            "time_ms": r.time_ms,
        }
        try:
            ok = _DB.record(item)
            if ok:
                recorded += 1
        except Exception:
            # swallow to keep endpoint robust; log inside recorder
            pass

    return QuizSubmitResponse(success=True, recorded=recorded)
