---

### `docs/guardrails.md`
```markdown
# Guardrails

We pre-check retrieval quality to avoid hallucinations and wasted LLM calls.

## Rule
- Compute `top_sim = max(doc.score)`.
- If `top_sim < min_similarity` → **do not call** the LLM.
- Return:
  ```json
  {
    "answer": "NEED_MORE_SOURCES",
    "citations": [],
    "citations_docs": [],
    "confidence": 0.0
  }