# Operations

## Deployments
- **GitHub Pages** for docs via `pages` workflow and `github-pages` environment.
- Backend/App deploys via separate workflows (TBD).

## Observability
- Minimal structured logs for `/rag/answer` to `/app/logs/app.json`.

## Runbooks
- **Pages build fails**  
  - Ensure `mkdocs.yml` has `site_name`, `site_url`, and Material theme installed.  
  - Re-run workflow: *Actions → Pages build and deployment → Re-run workflow*.
- **Tests failing suddenly**  
  - Check `/health` response shape and role progression logic.  
  - Confirm guardrail still runs before LLM.