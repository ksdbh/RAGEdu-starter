# Architecture

**Components:**
- **FastAPI app** (`backend/app/main.py`) – HTTP endpoints: health, auth demo, RAG, quiz.
- **RAG core** (`backend/app/rag.py`) – Search/LLM integration, guardrails, and test-friendly pipeline.
- **Tests** (`backend/tests/*`) – Contract for behavior and edge cases.

**Flow (high level):**
1. Request hits FastAPI (`/rag/answer`).
2. We build/fetch search results.
3. **Guardrail:** If similarity is too low, short-circuit with `NEED_MORE_SOURCES`.
4. Assemble prompt and call LLM.
5. Return answer + normalized citations + confidence.

This split lets us evolve RAG independently while keeping endpoints stable.