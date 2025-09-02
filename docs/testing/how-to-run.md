# How to run tests

Backend unit tests

```bash
cd backend
pytest -q
```

Common targets

- make backend-test — convenience wrapper (calls pytest in backend/)

CI tips

- Tests should not rely on real AWS services. Use stubs or localstack for integration tests.

Where to edit

!!! info "Where to edit"
    Source: docs/testing/how-to-run.md
    Tests: backend/tests/
