# How to run tests

Backend unit tests (pytest)

```bash
cd backend
pytest -q
# or use Makefile
make backend-test
```

Running a single test file

```bash
cd backend
pytest -q tests/test_rag.py::test_rag_answer
```

CI notes

- GitHub Actions workflows run pytest and build frontend artifacts. Check .github/workflows for details.

Where to edit

!!! info "Where to edit"
- Test runner docs: docs/testing/how-to-run.md
- Tests: backend/tests/
