# Architecture

This page explains how EduRAG is put together and how data flows through the system.

At the highest level there are two main phases:

- **Ingestion** — turn course materials (PDFs/slides) into semantically searchable chunks.
- **Query time** — turn a user question into an answer grounded in retrieved chunks.

## Components

### Backend (FastAPI)

Python package under `backend/app/`:

- `main.py` — defines the FastAPI app, routes (`/health`, `/whoami`, `/rag/answer`, quiz endpoints), and JSON logging.
- `rag.py` — implements the RAG orchestration (`answer_query`) including guardrails and citation normalization.
- `ingest.py` — provides chunking helpers (`semantic_chunk_text`, `chunk_pages`), `StubEmbeddings`, and an OpenSearch index helper.
- `auth.py` — mock and real Cognito client interfaces and FastAPI dependencies (`get_current_user`, `require_role`).
- `db.py` — a simple `CourseSyllabusStore` with in-memory and DynamoDB-backed behavior.
- `llm/adapter.py` — LLM abstraction with a deterministic `StubLLM` and a placeholder `BedrockLLM`.

### Frontend (Next.js)

- Lives in `frontend/`.
- Talks to the backend via `NEXT_PUBLIC_BACKEND_URL`.
- Renders chat-like interactions and shows citations for RAG answers.

### Infra & data plane

- **Vector store** — OpenSearch (or a stub) holds chunk embeddings and metadata.
- **Object storage** — S3 (or S3-like) for raw documents.
- **Auth** — Cognito in production (mocked locally).
- **Terraform** — under `infra/terraform` for S3, DynamoDB, and OpenSearch scaffolding.

## Ingestion flow

```mermaid
flowchart LR
  A[Upload PDFs / slides] --> B[Extract text (Textract / parser)]
  B --> C[Chunk pages + sections]
  C --> D[Compute embeddings]
  D --> E[(OpenSearch index)]
```

1. **Upload**: PDFs/slides land in S3 or are supplied directly to the ingest CLI.
2. **Extract**: Textract or a PDF parser turns them into raw text.
3. **Chunk**: `chunk_pages` attaches page and section metadata and splits into manageable chunks.
4. **Embed**: `StubEmbeddings` or a real embedding model encodes chunks into vectors.
5. **Index**: vectors and metadata are stored in OpenSearch for fast similarity search.

All of this logic is centralized in `backend/app/ingest.py` plus infra in `infra/`.

## Query-time RAG flow

```mermaid
flowchart LR
  U[User question] --> FE[Next.js frontend]
  FE --> API[/rag/answer]
  API --> S[Search client]
  S -->|docs| G{Guardrail}
  G --low score--> N[NEED_MORE_SOURCES]
  G --ok--> P[Prompt builder]
  P --> L[LLM provider]
  L --> R[Answer + citations]
  R --> FE
```

1. **Question in**: the frontend (or an API client) sends a POST to `/rag/answer` with `query` (or `question` in tests).
2. **Search**: a search client returns top-k snippets (title, page, snippet, score).
3. **Guardrail**: `answer_query` checks the highest score against `min_similarity`.
   - If it is too low, it returns `NEED_MORE_SOURCES` without calling the LLM.
4. **Prompt build**: otherwise, a prompt containing the top snippets and a `Sources:` line is composed.
5. **LLM call**: the LLM provider (usually `StubLLM` in dev) produces an answer string.
6. **Citations**: normalized citation objects are returned so the frontend can render sources clearly.

## Design choices (scaffold)

| Concern      | Choice (scaffold)                   | Rationale                                                |
|--------------|--------------------------------------|----------------------------------------------------------|
| Embeddings   | Stub / OpenAI / Bedrock (pluggable) | Provider-agnostic; stub makes tests deterministic.       |
| Vector store | OpenSearch (or stub)                | Well-known vector-capable store; Terraform examples.     |
| AuthN/Z      | Cognito (mock in dev)               | Aligns with AWS-native identity; mock keeps dev simple.  |

In a real deployment you can swap stubs for production services while keeping the same high-level flow.

---

!!! info "Where to edit"
    Source: `docs/architecture.md`  
    Key modules: `backend/app/ingest.py`, `backend/app/rag.py`, `backend/app/main.py`
