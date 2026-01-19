# How the Assistant Uses Docs

The assistant composes prompts that include retrieved passages from this documentation and from ingested course materials, then returns answers with citations.

## Prompt construction

When using EduRAG as a backend:

- Retrieved snippets from the vector store (course chunks) are included as bullet points.
- Documentation snippets may also be included when answering platform questions.
- A `Sources:` section is appended to the prompt to nudge the LLM to keep answers grounded.

## Doc design guidance

To keep this site assistant-friendly:

- **Annotate chunks** with page, section, or endpoint names when possible.
- Keep paragraphs short and focused so they make good RAG chunks.
- Use clear headings for each concept (e.g., *Guardrails*, *Environments*, *RAG Overview*).

## Frontend behavior

The frontend is expected to:

- Render answers alongside **citations** that point back to either course content or relevant docs pages.
- Optionally provide links to the original documents or doc anchors so users can verify context themselves.

---

!!! info "Where to edit"
    Source: `docs/assistant/how-it-uses-docs.md`  
    Code: `backend/app/rag.py`, `frontend/`
