# Guardrails for RAG (safety & grounding)

This page explains guardrails to keep LLM outputs safe and grounded.

Guidelines

- Always include citations from retrieved chunks in the response.
- If the top passages do not contain an answer, reply with a safe fallback like "I don't know — please consult the materials." Do not hallucinate facts.
- Enforce token and length limits on prompts and responses.

Where to implement

- Implement guardrails in the QA orchestration (answer_query) to validate LLM output and attach sources.

Where to edit

!!! info "Where to edit"
- Guardrails: backend/app/rag.py -> function answer_query
- Tests: backend/tests/test_rag_guardrails.py <!-- TODO: add tests -->
