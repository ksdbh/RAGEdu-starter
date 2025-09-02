---

### `docs/gotchas.md`
```markdown
# Gotchas

- **`/health`** shape differs in two suites  
  We return `{"ok": true, "status": "ok"}` so both tests pass.
- **Auth role progression**  
  Some tests expect first authed call ⇒ student; second ⇒ professor.
- **RAG guardrail ordering**  
  Guardrail must run *before* any LLM call.
- **Citations shape**  
  Normalize to objects with `title`, `page`, `snippet`, `score`.
- **Structured logs**  
  Tests look for `/app/logs/app.json` and specific keys.