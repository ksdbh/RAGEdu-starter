# How the Assistant Uses Docs

The assistant composes prompts that include retrieved passages and citation markers. The frontend shows citations so users can verify the grounding of answers.

Design guidance

- Keep chunks annotated with page and section metadata to support in-UI citations.
- Surface a link or download to the source document when returning an answer if possible.

Where to edit

!!! info "Where to edit"
    Source: docs/assistant/how-it-uses-docs.md
    Code: backend/app/rag.py, frontend/
