from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import os
import json
import time
import logging

logger = logging.getLogger("rag")

router = APIRouter(prefix="/rag")

# Simple request model
class RAGRequest(BaseModel):
    question: str
    top_k: Optional[int] = 4
    language: Optional[str] = None  # TODO: use this for language validation/detection


# --- Minimal internal stubs (kept simple for the scaffold) ---
def _retrieve_documents(question: str, top_k: int = 4) -> List[Dict[str, Any]]:
    """Placeholder retrieval function. In the real system this would query
    OpenSearch / vector DB and return top-k passages with metadata.
    """
    # Return a deterministic small stub so unit tests can assert shape
    return [
        {"id": "doc1", "text": f"Stub passage for: {question}", "score": 0.9}
    ][:top_k]


def _compose_prompt(question: str, passages: List[Dict[str, Any]]) -> str:
    """Compose a simple prompt for the LLM from question + passages.
    Real implementations should build a careful prompt including citations.
    """
    joined = "\n\n".join([p.get("text", "") for p in passages])
    return f"Use the following passages to answer the question. Passages:\n{joined}\n\nQuestion: {question}\nAnswer:"


def _call_llm(prompt: str) -> str:
    """Placeholder LLM call. Replace with real OpenAI/Bedrock client calls.
    Keep it deterministic for unit tests.
    """
    # Very small deterministic stubbed reply
    return "This is a stubbed answer based on provided passages."


# --- Structured logging helper ---

def _write_structured_log(entry: Dict[str, Any]) -> None:
    """Append a single JSON object (one-per-line) to logs/app.json.

    The scan-logs workflow expects newline-delimited JSON in logs/app.json.
    """
    try:
        logs_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        path = os.path.join(logs_dir, "app.json")
        # attach a timestamp
        entry.setdefault("ts", int(time.time()))
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        # Logging must not raise; swallow errors but emit to the standard logger
        logger.exception("Failed to write structured log")


# --- Endpoint implementation with validation + error handling ---
@router.post("/answer")
async def answer(req: RAGRequest, request: Request):
    question = (req.question or "").strip()

    # Validation: non-empty
    if not question:
        raise HTTPException(status_code=400, detail="Question must be non-empty")

    # Validation: max length (simple safeguard)
    MAX_LEN = 1000
    if len(question) > MAX_LEN:
        raise HTTPException(status_code=400, detail=f"Question too long (max {MAX_LEN} characters)")

    # TODO: language check - ensure question is in supported language(s)
    # For now we accept any language but the TODO indicates future work.

    # Prepare a structured log entry we will enrich depending on success/failure
    log_entry: Dict[str, Any] = {
        "route": "/rag/answer",
        "question_len": len(question),
        "top_k": req.top_k,
        "client_addr": request.client.host if request.client else None,
    }

    try:
        # Retrieval + LLM calls are wrapped so any error produces a user-facing
        # fallback message rather than an internal 500 stacktrace leak.
        passages = _retrieve_documents(question, top_k=req.top_k or 4)
        prompt = _compose_prompt(question, passages)
        answer_text = _call_llm(prompt)

        log_entry.update({"status": "ok", "passages_returned": len(passages)})
        _write_structured_log(log_entry)

        return {"answer": answer_text, "passages": passages}

    except Exception as exc:
        # Log structured error details for the nightly scan-logs workflow.
        log_entry.update({
            "status": "error",
            "error_type": type(exc).__name__,
            "error_msg": str(exc),
        })
        _write_structured_log(log_entry)

        # Return a safe, user-facing fallback message.
        # Keep the message generic to avoid leaking internal error details.
        raise HTTPException(
            status_code=500,
            detail="Sorry, I couldn't answer that right now. Please try again later.",
        )
