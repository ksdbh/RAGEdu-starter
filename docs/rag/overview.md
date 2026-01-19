# RAG Overview

Retrieval-Augmented Generation (RAG) means **retrieving** relevant context before you **generate** an answer.

EduRAG’s RAG implementation focuses on:

- Keeping answers grounded in specific course documents.
- Returning usable citations so users can verify the answer.
- Exposing clear extension points for real-world deployments.

## Building blocks

- **Ingest** — parse PDFs/slides into text and split into chunks with rich metadata.
- **Embeddings** — turn each chunk into a vector in an embedding space.
- **Index** — store vectors and metadata in OpenSearch.
- **Retrieve** — for a given question, fetch the top-k most similar chunks.
- **Compose** — build a prompt that includes the retrieved chunks and a `Sources:` section.
- **Generate** — call an LLM to synthesize a short answer.

## Guardrails

EduRAG has a built-in guardrail in `backend/app/rag.py`:

- Compute `top_sim = max(score)` over all retrieved docs.
- If `top_sim < min_similarity`, do **not** call the LLM.
- Instead, return a special answer code (`NEED_MORE_SOURCES`) and empty citations.

This behavior is enforced by tests and prevents wasting LLM calls on low-quality evidence.

## Example RAG call

Request (simplified):

```json
POST /rag/answer
{
  "query": "What topics does this course cover?",
  "top_k": 5
}
```

Successful response shape:

```json
{
  "answer": "ANSWER based on retrieved docs: ...",
  "citations": [
    {"title": "Doc 1", "page": 1, "snippet": "Context A", "score": 0.9},
    {"title": "Doc 2", "page": 2, "snippet": "Context B", "score": 0.8}
  ],
  "metadata": {
    "top_k": 5,
    "course_id": null,
    "confidence": 0.9
  }
}
```

If the guardrail fires you will instead see:

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

For a step-by-step walkthrough of how chunks are created, see [Ingestion](ingestion.md), [Chunking](chunking.md), and [Embeddings](embeddings.md).

---

!!! info "Where to edit"
    Source: `docs/rag/overview.md`  
    Code: `backend/app/ingest.py`, `backend/app/rag.py`
