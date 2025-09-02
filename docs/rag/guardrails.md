# Guardrails

Purpose

Guardrails reduce hallucination and expose provenance for answers. They include:

- Retrieval: always include citations from top-k passages.
- Prompting: instruct LLM to cite passages verbatim and refuse to answer out-of-domain questions.
- Post-processing: sanitize or redact PII before returning.

Where to edit

!!! info "Where to edit"
    Source: docs/rag/guardrails.md
    Implementation: backend/app/rag.py :: answer_query

!!! note
    If answer_query is not present, implement a function that validates inputs, retrieves passages, composes a prompt with explicit citation markers, calls the LLM client, and returns structured JSON with sources.
