# RAG Pipeline

This page explains how EduRAG’s Retrieval-Augmented Generation (RAG) flow works end-to-end.

## High-level flow

1. **Query in** → the client sends a POST to `/rag/answer` with `query` (or `question` for some tests).
2. **Search** → a search client returns a list of snippet-like documents (title, page, snippet, score).
3. **Guardrail** → `answer_query` checks similarity; if the best score is too low, it bails out early.
4. **Prompting** → a grounded prompt is constructed, including a `Sources:` line.
5. **LLM** → an LLM provider (stub or real) synthesizes an answer.
6. **Citations** → normalized `{ title, page, snippet, score }` items are returned for the UI.

```mermaid
flowchart LR
    A[Client] --> B[/rag/answer]
    B --> C[Search client]
    C -->|docs| D{Guardrail}
    D --low--> E[NEED_MORE_SOURCES]
    D --ok--> F[Prompt builder]
    F --> G[LLM]
    G --> H[Answer + citations]
```

## Search client contracts

`backend/app/rag.py::answer_query` is intentionally tolerant of several search client signatures, including:

- `search(query, top_k=..., rerank=...) -> list[dict]`
- `search(query) -> list[dict]`
- OpenSearch-style: `search(index=?, body={...}) -> {"hits": {"hits": [...]}}`

Results are normalized into a consistent internal format so the rest of the pipeline does not care which concrete client you use.

## Prompt structure

The prompt built for the LLM includes:

- A short instruction to use **only** the retrieved context.
- A bullet list of snippets.
- The question.
- A `Sources:` cue so answers are expected to reference retrieved snippets.

Tests assert that the final answer string begins with `"ANSWER based on"` in the happy path.

## Citations

The API response exposes citations in a normalized shape:

```json
{
  "title": "Doc 1",
  "page": 1,
  "snippet": "Context A",
  "score": 0.9
}
```

The frontend can render these inline with the answer, or as a separate “Sources” section.

---

For a conceptual overview start with [RAG Overview](rag/overview.md). For implementation details, see `backend/app/rag.py` and the RAG-related tests in `backend/tests/`.
