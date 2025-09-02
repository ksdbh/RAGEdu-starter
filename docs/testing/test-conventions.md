# Test conventions

- Use pytest fixtures for shared resources.
- Name tests clearly: test_<unit>__<condition>__<expected>().
- Keep unit tests fast and deterministic — use StubEmbeddings for embeddings.
- For API tests: use TestClient from FastAPI (backend/app/main.py) and include auth headers with mock tokens.

Example test snippet

```python
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_whoami_student():
    resp = client.get("/whoami", headers={"Authorization": "Bearer student_token"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "student"
```

Where to edit

!!! info "Where to edit"
    Source: docs/testing/test-conventions.md
    Tests: backend/tests/
