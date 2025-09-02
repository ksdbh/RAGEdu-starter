# RAG Pipeline

This page explains how our Retrieval-Augmented Generation (RAG) flow works end-to-end.

## High-level Flow
1. **Query in** → request hits `/rag/answer` with `query` (or `question` in tests).
2. **Search** → a search client returns top-k snippets (title, page, score, snippet).
3. **Guardrail** → if top similarity < threshold, return `NEED_MORE_SOURCES` (no LLM call).
4. **Prompting** → build a grounded prompt (must include *“Sources:”* cue).
5. **LLM** → synthesize answer using only retrieved snippets.
6. **Citations** → return normalized `{ title, page, snippet, score }` items.

```mermaid
flowchart LR
    A[Client] --> B[/rag/answer/]
    B --> C[Search Client]
    C -->|docs| D{Guardrail}
    D --low--> E[NEED_MORE_SOURCES]
    D --ok--> F[Prompt Builder]
    F --> G[LLM]
    G --> H[Answer + Citations]