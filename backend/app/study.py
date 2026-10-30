"""Explicit demo and local-corpus Q&A runtimes."""
from __future__ import annotations

import os
from fastapi import HTTPException

from .local_index import LocalIndex, validate_course_id
from .rag import GUARDRAIL_NEED_MORE_SOURCES, answer_query


class DemoSearch:
    def search(self, query: str):
        return [
            {"title": f"Doc {i}", "page": i, "snippet": f"Context {letter}", "score": score}
            for i, letter, score in [(1, "A", 0.9), (2, "B", 0.8), (3, "C", 0.7)]
        ]


class DemoLLM:
    def generate(self, prompt: str) -> str:
        return "ANSWER based on provided context: stubbed answer."


class RetrievedPassages:
    def __init__(self, passages):
        self.passages = passages

    def search(self, query: str):
        return self.passages


class SourceExcerpts:
    def generate(self, prompt: str) -> str:
        return "Matching course passages are quoted in the citations. No model synthesis was used."


class StudyService:
    def __init__(self, mode: str, index_path: str):
        if mode not in {"demo", "local"}:
            raise ValueError("RAGEDU_MODE must be demo or local")
        self.mode = mode
        self.index = LocalIndex(index_path)

    def status(self):
        return {
            "mode": self.mode,
            "courses": self.index.courses() if self.mode == "local" else [],
            "retrieval": "keyword" if self.mode == "local" else "simulated",
            "generation": "source_excerpts" if self.mode == "local" else "simulated",
        }

    def answer(self, question: str, *, course_id: str | None, top_k: int):
        if self.mode == "local":
            if not course_id:
                raise ValueError("Select a course_id for local retrieval")
            course_id = validate_course_id(course_id)
            # Read before core orchestration so storage faults become 503 rather
            # than being confused with an ordinary no-match result.
            passages = self.index.search(question, course_id=course_id, top_k=top_k)
            search, llm, threshold = RetrievedPassages(passages), SourceExcerpts(), 0.25
        else:
            search, llm, threshold = DemoSearch(), DemoLLM(), 0.1
        result = answer_query(question, search_client=search, llm_client=llm,
                              top_k=top_k, rerank=False, min_similarity=threshold)
        insufficient = result["answer"] == GUARDRAIL_NEED_MORE_SOURCES
        answer = "Not enough context to answer confidently." if insufficient else result["answer"]
        if self.mode == "local" and not insufficient:
            answer = "Matching source excerpts (no model synthesis):\n\n" + "\n\n".join(
                f'[{citation["title"]}, page {citation["page"]}] {citation["snippet"]}'
                for citation in result["citations"]
            )
        return {
            "answer": answer,
            "citations": result["citations"],
            "metadata": {
                "mode": self.mode, "course_id": course_id, "top_k": top_k,
                "confidence": result["confidence"],
                "status": "insufficient_evidence" if insufficient else "ok",
                "retrieval": "keyword" if self.mode == "local" else "simulated",
                "generation": "source_excerpts" if self.mode == "local" else "simulated",
            },
        }


def get_study_service() -> StudyService:
    # No cached connection: imports by the CLI become visible to a running API.
    try:
        return StudyService(os.environ.get("RAGEDU_MODE", "demo"),
                            os.environ.get("RAGEDU_INDEX_PATH", "data/courses.sqlite3"))
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
