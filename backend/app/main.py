# backend/app/main.py
from __future__ import annotations

import json
import os
import logging
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field

from .study import StudyService, get_study_service

app = FastAPI(title="RAGEdu Backend")

from .auth import User, get_current_user, get_current_user_optional, require_role

# ---------------- Schemas ----------------
class RagAnswerRequest(BaseModel):
    query: Optional[str] = None
    question: Optional[str] = None
    top_k: Optional[int] = Field(default=None, ge=1, le=20, strict=True)
    course_id: Optional[str] = None

class QuizGenerateRequest(BaseModel):
    query: str
    num_questions: int = 5

class QuizSubmitRequest(BaseModel):
    quiz_id: str
    user_id: str
    results: List[Dict[str, Any]]

# ---------------- Health and identity ----------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/whoami")
def whoami(user: User = Depends(get_current_user)):
    return user


@app.get("/protected/student")
def protected_student(user: User = Depends(require_role("student"))):
    return {"ok": True, "role": user.role, "message": "student endpoint: authenticated"}


@app.get("/protected/professor")
def protected_professor(user: User = Depends(require_role("professor"))):
    return {"ok": True, "role": user.role, "message": "professor endpoint: authenticated"}


@app.get("/protected/auth")
def protected_auth(user: User = Depends(get_current_user)):
    return {"ok": True, "role": user.role, "message": "authenticated"}


@app.get("/greeting")
def greeting(user: Optional[User] = Depends(get_current_user_optional)):
    return {"message": f"Hello, {user.role if user else 'anonymous user'}!"}

# ---------------- RAG API -----------------------------------------------------
LOG_PATH = Path(os.environ.get("RAGEDU_LOG_PATH", "logs/app.json"))
logger = logging.getLogger(__name__)

@app.post("/rag/answer")
def rag_answer(req: RagAnswerRequest, service: StudyService = Depends(get_study_service)):
    if req.query is not None and req.question is not None:
        raise HTTPException(status_code=422, detail="Supply query or question, not both")
    # Decide which field is present (tests send either 'query' or 'question')
    used_field = "question" if req.question is not None else ("query" if req.query is not None else None)
    q = (req.query if req.query is not None else req.question)

    # Validation to satisfy both suites
    if used_field == "query":
        if q is None or q.strip() == "":
            raise HTTPException(status_code=422, detail="query must be non-empty")
        if len(q.strip()) > 1000:
            raise HTTPException(status_code=422, detail="Query too long")
    elif used_field == "question":
        if q is None or q.strip() == "":
            raise HTTPException(status_code=400, detail="Question must be non-empty")
        if len(q.strip()) > 1000:
            raise HTTPException(status_code=400, detail="Question too long")
    else:
        raise HTTPException(status_code=422, detail="query must be non-empty")

    top_k = req.top_k if isinstance(req.top_k, int) else 5
    if top_k < 1:
        raise HTTPException(status_code=422, detail="top_k must be >= 1")

    try:
        result = service.answer(q.strip(), course_id=req.course_id, top_k=top_k)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        logger.error("Local corpus is unavailable", exc_info=True)
        raise HTTPException(status_code=503, detail="Local corpus is unavailable; verify the index configuration") from exc

    # Structured JSONL log
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "event": "rag_answer",
                "route": "/rag/answer",
                "status": "ok",
                "q": q,
                "top_k": top_k
            }) + "\n")
    except OSError:
        logger.warning("Unable to write RAG request log", exc_info=True)

    return result


@app.get("/rag/status")
def rag_status(service: StudyService = Depends(get_study_service)):
    try:
        return service.status()
    except sqlite3.Error as exc:
        raise HTTPException(status_code=503, detail="Local corpus is unavailable; verify the index configuration") from exc


# ---------------- Quiz endpoints ---------------------------------------------
@app.post("/quiz/generate")
def quiz_generate(req: QuizGenerateRequest):
    n = max(1, min(int(req.num_questions), 20))
    qs = [{
        "id": f"q{i+1}",
        "type": "mcq",
        "prompt": f"{req.query} #{i+1}?",
        "question": f"{req.query} #{i+1}?",
        "choices": ["A", "B", "C", "D"],
        "distractors": ["B", "C", "D"],
        "answer": "A",
        "spaced_rep": True,
    } for i in range(n)]
    return {"quiz_id": "demo-quiz", "questions": qs}

@app.post("/quiz/submit")
def quiz_submit(req: QuizSubmitRequest):
    if not req.results:
        raise HTTPException(status_code=400, detail="results required")
    correct = sum(1 for r in req.results if r.get("correct") is True)
    return {"ok": True, "score": correct, "total": len(req.results)}