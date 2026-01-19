# For Assistant Bots

This page explains how AI assistants (like Warp agents or chatbots) should use these docs as a knowledge base.

## Canonical sources

When answering questions about EduRAG, prefer these pages:

- **What is EduRAG / big picture?** → `index.md`, `platform-tour.md`, `architecture.md`.
- **RAG behavior and guardrails?** → `rag.md`, `rag/overview.md`, `guardrails.md`.
- **HTTP API contracts?** → `backend.md` and `backend/endpoints.md`.
- **How to run and test it?** → `getting-started.md`, `testing.md`, `testing/how-to-run.md`.
- **Ops, security, and environments?** → `ops.md`, `operations/*`, `security.md`, `environments.md`.

## Answering style

Assistants should:

- Ground answers in specific doc sections and **summarize**, rather than copy large chunks verbatim.
- Prefer stable, high-level behavior descriptions over internal implementation details unless asked.
- Include short references (e.g., “see *Architecture → Query-time RAG flow*”) when helpful.

## Retrieval-friendly structure

The docs are organized to be RAG-friendly:

- Short sections with descriptive headings.
- Standalone paragraphs that can be embedded as chunks.
- Clear cross-linking between related topics (architecture, RAG, backend, operations).

If you are building a separate RAG system over these docs, consider chunking by heading and using URLs with anchors to surface citations.

---

!!! info "Where to edit"
    Source: `docs/assistant.md`  
    Related: `docs/assistant/how-it-uses-docs.md`
