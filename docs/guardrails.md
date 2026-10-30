# Guardrails

> Updated 2026-10-30: the [current handoff](changelog.md) and [local PDF search guide](guides/local-course-search.md) describe verified behavior. The active API explicitly selects a simulated demo or persistent course-scoped keyword/source-excerpt search. Older cloud/semantic design descriptions below may remain disconnected or planned; empty evidence never substitutes sources.

EduRAG includes a guardrail in the RAG pipeline to avoid hallucinations and unnecessary LLM calls.

## Rule

1. Compute `top_sim = max(doc.score)` across retrieved documents.
2. If `top_sim < min_similarity`:
   - **Do not call** the LLM provider.
   - Return a sentinel answer code instead.

JSON shape used by the core RAG helper (`backend/app/rag.py`):

```json
{
  "answer": "NEED_MORE_SOURCES",
  "citations": [],
  "citations_docs": [],
  "confidence": 0.0
}
```

The `/rag/answer` HTTP endpoint wraps this behavior with a more user-friendly message:

```json
{
  "answer": "Not enough context to answer confidently.",
  "citations": [],
  "metadata": {
    "top_k": 5,
    "course_id": null,
    "confidence": 0.0
  }
}
```

## Why this matters

- Prevents sending low-quality prompts to the LLM (saves cost and reduces noise).
- Makes it explicit to the user when more or better documents are required.
- Is enforced with tests that ensure the LLM is not called when similarity is below the threshold.

---

!!! info "Where to edit"
    Source: `docs/guardrails.md`  
    Implementation: `backend/app/rag.py`  
    Tests: `backend/tests/test_rag.py`, `backend/tests/test_rag_answer.py`
